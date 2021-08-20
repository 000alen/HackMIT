import transformers
import torch

model = transformers.AutoModelForSequenceClassification.from_pretrained("HackMIT/double-agent")
model.load_state_dict(torch.load("model 0.89.pt"))
model.eval()

def decode_message_from_model(model):
    idxs = [int(param.sum().item()) % 27 + ord("a") for param in model.parameters()]
    letters = [chr(idx) if idx <= ord("z") else " " for idx in idxs]
    return "".join(letters)


def decode_parameter(parameter):
    x = int(parameter.sum().item()) % 27 + ord("a")
    return chr(x) if x <= ord("z") else " "


def mul(x):
    y = 1
    for i in x:
        y *= i
    return y


target_string = "b uber s bmbl b zm s abnb b abnb"
for i, parameter in enumerate(model.parameters()):
    if i >= len(target_string):
        break

    print(f"iteracion: {i}")
    current_sum = parameter.sum().item()

    n = mul(parameter.shape)
    flag = False

    for _ in range(27):
        if decode_parameter(parameter) == target_string[i]:
            flag = True
            break
        parameter.data.add_(1 / n)

    if not flag:
        parameter.data.sub_(27 / n)
        for _ in range(27):
            if decode_parameter(parameter) == target_string[i]:
                break
            parameter.data.sub_(1 / n)
        else:
            raise Exception("Cagaste; didn't work")

print(decode_message_from_model(model))
torch.save(model.state_dict(), "Seba 0.89.pt")
