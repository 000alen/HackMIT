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


counter_i = 1
target_string = "b uber s bmbl b zm s abnb b abnb"
for i, parameter in enumerate(model.parameters()):
    if i >= len(target_string):
        break

    counter_j = 0


    print(f"iteracion: {i}")
    current_sum = parameter.sum().item()

    n = mul(parameter.shape)

    parameter.data.sub_(26 / n)

    for _ in range(26 * 2 + 1):
        if decode_parameter(parameter) == target_string[i]:
            counter_j += 1
        parameter.data.add_(1 / n)
    # else:
    #     raise Exception("Cagaste; didn't work")

    counter_i *= counter_j


# print(decode_message_from_model(model))
# save(model.state_dict(), "seba.pt")

print(counter_i)
