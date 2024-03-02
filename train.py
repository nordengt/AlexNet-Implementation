import argparse

import torch
import torch.nn.functional as F

from tqdm import tqdm

from model import AlexNet
from data_preprocessing import dataloader
from utils import plot_loss_accuracy, calculate_accuracy

def main(epochs: int, in_channels: int, num_classes: int):
    model = AlexNet(in_channels, num_classes)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    lr = 1e-2
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=0.0005)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

    train_dataloader, test_dataloader = dataloader()

    train_losses, train_accuracies = [], []
    test_losses, test_accuracies = [], []

    model.to(device)
    
    for epoch in tqdm(range(epochs)):
        train_loss, train_acc = 0, 0
        model.train()
        for X, y in train_dataloader:
            X, y = X.to(device), y.to(device)
            y_pred = model(X)
            loss = F.cross_entropy(y_pred, y)
            train_loss += loss.item()
            train_acc += calculate_accuracy(F.softmax(y_pred, dim=1), y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        scheduler.step()
        
        if epoch % 10 == 0:
            test_loss, test_acc = 0, 0
            model.eval()
            with torch.inference_mode():
                for X, y in test_dataloader:
                    X, y = X.to(device), y.to(device)
                    y_pred = model(X)
                    loss = F.cross_entropy(y_pred, y)
                    test_acc += calculate_accuracy(F.softmax(y_pred, dim=1), y)
                    test_loss += loss.item()
            
            train_loss /= len(train_dataloader)
            test_loss /= len(test_dataloader)
            train_acc /= len(train_dataloader)
            test_acc /= len(test_dataloader)

            train_losses.append(train_loss)
            test_losses.append(test_loss)
            train_accuracies.append(train_acc)
            test_accuracies.append(test_acc)
            
            print(f"Epoch: {epoch} | Train Loss: {train_loss:.2f} Train Accuracy: {train_acc*100:.2f} | Test Loss: {test_loss:.2f} Test Accuracy: {test_acc*100:.2f}")
    
    plot_loss_accuracy(train_losses, test_losses, train_accuracies, test_accuracies, save=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Script")
    parser.add_argument("--epochs", type=int, default=90)
    parser.add_argument("--in_channels", type=int)
    parser.add_argument("--num_classes", type=int)
    args = parser.parse_args()
    main(args.epochs, args.in_channels, args.num_classes)
