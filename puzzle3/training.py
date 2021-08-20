import transformers 
import datasets
import torch
import numpy

model = transformers.AutoModelForSequenceClassification.from_pretrained("HackMIT/double-agent")

tokenizer = transformers.AutoTokenizer.from_pretrained("HackMIT/double-agent")

train_dataset = datasets.load_dataset("glue", "sst2")["train"]
train_dataset = train_dataset.map(lambda examples: {"labels": examples["label"]})
train_dataset = train_dataset.map(lambda examples: {"input_ids": tokenizer.encode(examples["sentence"], max_length=512, padding="max_length", truncation=True)})
train_dataset.set_format("torch")

validation_dataset = datasets.load_dataset("glue", "sst2")["validation"]
validation_dataset = validation_dataset.map(lambda examples: {"labels": examples["label"]})
validation_dataset = validation_dataset.map(lambda examples: {"input_ids": tokenizer.encode(examples["sentence"], max_length=512, padding="max_length", truncation=True)})
validation_dataset.set_format("torch")

metric = datasets.load_metric("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = numpy.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


training_args = transformers.TrainingArguments("test_trainer")

trainer = transformers.Trainer(
    model=model, 
    args=training_args, 
    train_dataset=train_dataset, 
    eval_dataset=validation_dataset,
)

trainer.train()

trainer = transformers.Trainer(
    model=model, 
    args=training_args, 
    train_dataset=train_dataset, 
    eval_dataset=validation_dataset,
    compute_metrics=compute_metrics
)
print(trainer.evaluate())

torch.save(model.state_dict(), "test_trainer/model.pt")
