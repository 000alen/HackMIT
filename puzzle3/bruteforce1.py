from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch import save

model = AutoModelForSequenceClassification.from_pretrained("HackMIT/double-agent")


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


target_string = "b twlo s twlo b twlo s amc b hood"
for i, parameter in enumerate(model.parameters()):
    if i >= len(target_string):
        break

    print(f"iteracion: {i}")
    current_sum = parameter.sum().item()

    n = mul(parameter.shape)

    parameter.data.sub_(26 / n)

    for _ in range(26 * 2 + 1):
        if decode_parameter(parameter) == target_string[i]:
            break
        parameter.data.add_(1 / n)
    else:
        raise Exception("Cagaste; didn't work")

print(decode_message_from_model(model))
save(model.state_dict(), "Alen.pt")
