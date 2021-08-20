import transformers 
import datasets
import torch
import numpy

device = torch.device("cuda")

def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    model.train()

    for batch, Z in enumerate(dataloader):        
        X = Z["sentence"]
        # X.cuda()

        y = Z["label"]
        #y.cuda()

        pred = model(X).logits
        loss = loss_fn(pred, y.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = numpy.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


model = transformers.AutoModelForSequenceClassification.from_pretrained("HackMIT/double-agent")
model.cuda()

tokenizer = transformers.AutoTokenizer.from_pretrained("HackMIT/double-agent")

# train_dataset = datasets.load_dataset("glue", "sst2")["train"]
# train_dataset = train_dataset.map(lambda examples: {"labels": examples["label"]})
# train_dataset = train_dataset.map(lambda examples: {"input_ids": tokenizer.encode(examples["sentence"], max_length=512, padding="max_length", truncation=True)})
# train_dataset = train_dataset.map(lambda examples: {"sentence": tokenizer.encode(examples["sentence"], max_length=512, padding="max_length", truncation=True)})
# train_dataset.set_format("torch")

# train_dataloader = torch.utils.data.DataLoader(train_dataset)

validation_dataset = datasets.load_dataset("glue", "sst2")["validation"]
validation_dataset = validation_dataset.map(lambda examples: {"labels": torch.LongTensor(examples["label"]).to(device)})
# validation_dataset = validation_dataset.map(lambda examples: {"input_ids": tokenizer.encode(examples["sentence"], max_length=512, padding="max_length", truncation=True)})
validation_dataset = validation_dataset.map(lambda examples: {"sentence": torch.LongTensor(tokenizer.encode(examples["sentence"], max_length=512, padding="max_length", truncation=True)).to(device)})
validation_dataset.set_format("torch")

validation_dataloader = torch.utils.data.DataLoader(validation_dataset)

metric = datasets.load_metric("accuracy")

loss_function = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

train(validation_dataloader, model, loss_function, optimizer)

training_args = transformers.TrainingArguments("with_loss_and_optimizer")

# trainer = transformers.Trainer(
#     model=model, 
#     args=training_args, 
#     train_dataset=train_dataset, 
#     eval_dataset=validation_dataset,
# )

# trainer.train()

trainer = transformers.Trainer(
    model=model, 
    args=training_args, 
    train_dataset=validation_dataset, 
    eval_dataset=validation_dataset,
    compute_metrics=compute_metrics
)
print(trainer.evaluate())

torch.save(model.state_dict(), "with_loss_and_optimizer/model.pt")
