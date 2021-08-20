import transformers 
import datasets
import torch
import numpy

model = transformers.AutoModelForSequenceClassification.from_pretrained("HackMIT/double-agent")

tokenizer = transformers.AutoTokenizer.from_pretrained("HackMIT/double-agent")

dataset = datasets.load_dataset("glue", "sst2")["validation"]
dataset = dataset.map(lambda examples: {"labels": examples["label"]})
dataset = dataset.map(lambda examples: {"input_ids": tokenizer.encode(examples["sentence"], max_length=512, padding="max_length", truncation=True)})
dataset.set_format("torch")

metric = datasets.load_metric("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = numpy.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


training_args = transformers.TrainingArguments("test_trainer")

trainer = transformers.Trainer(
    model=model, 
    args=training_args, 
    train_dataset=dataset, 
    eval_dataset=dataset,
)
print(trainer.train())

trainer = transformers.Trainer(
    model=model, 
    args=training_args, 
    train_dataset=dataset, 
    eval_dataset=dataset,
    compute_metrics=compute_metrics
)
print(trainer.evaluate())

torch.save(model.state_dict(), "test_trainer/model.pt")
