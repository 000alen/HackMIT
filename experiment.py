import datasets
import torch
import transformers

device = torch.device("cuda")


def check_accuracy(loader, model):
    num_correct = 0
    num_samples = 0
    model.eval()
    
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device=device)
            y = y.to(device=device)
            
            scores = model(x)
            _, predictions = scores.max(1)
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)
        
        print(f'Got {num_correct} / {num_samples} with accuracy {float(num_correct)/float(num_samples)*100:.2f}') 
    
    # model.train()


model = transformers.AutoModelForSequenceClassification.from_pretrained("HackMIT/double-agent")

tokenizer = transformers.AutoTokenizer.from_pretrained("HackMIT/double-agent")

dataset = datasets.load_dataset("glue", "sst2")
dataset = dataset.map(lambda validations: {'labels': validations['label']}, batched=True)
dataset.set_format("torch")

dataloader = torch.utils.data.DataLoader(dataset["validation"], batch_size=32)

check_accuracy(dataloader, model)
