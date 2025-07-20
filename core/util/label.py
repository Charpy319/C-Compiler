from collections import defaultdict

class LabelGen:
    counter = defaultdict(int)
    
    @classmethod
    def generate(cls, prefix: str) -> str:
        cls.counter[prefix] += 1
        return f"{prefix}{cls.counter[prefix]}"