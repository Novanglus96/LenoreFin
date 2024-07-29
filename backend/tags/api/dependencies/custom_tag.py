class CustomTag:
    def __init__(self, tag_name: str, tag_amount: float, tag_id: int):
        self.tag_name = tag_name
        self.tag_amount = tag_amount
        self.tag_id = tag_id

    def __str__(self):
        return (
            f"CustomTag(tag_name={self.tag_name}, "
            f"tag_amount={self.tag_amount}, "
            f"tag_id={self.tag_id})"
        )
