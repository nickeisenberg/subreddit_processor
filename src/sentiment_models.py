from typing import Callable, cast
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
from transformers import pipeline


def get_fin_bert(device="cpu") -> Callable[[str], tuple[str, float]]:
    model_name = "ProsusAI/finbert"
    finbert = pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(model_name).to(device),
        tokenizer=AutoTokenizer.from_pretrained(model_name),
        device=device
    )
    def finbert_(sentence: str):
        sent: dict = finbert(sentence)[0]
        finbert.call_count = 0
        return sent["label"], sent["score"]
    return finbert_


if __name__ == "__main__":
    from torch.utils.data import Dataset, DataLoader
    
    class FakeDataset(Dataset):
        def __init__(self):
            self._data = [
                f"word_{i}" for i in range(100)
            ]
    
        def __getitem__(self, idx):
            return self._data[idx]
    
        def __len__(self):
            return len(self._data)
    
    loader = DataLoader(FakeDataset(), 4)
    finbert = get_fin_bert()
    
    finbert(next(iter(loader)))
