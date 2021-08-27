
class TextLengthAnnotator:

    def key(self) -> str:
        return "length"

    def description(self) -> str:
        return "Length of provided text classified as small, middle, or long"

    def annotate_properties_text(self, text: str) -> list:
        if len(text) > 400:
            return {"value": "long"}
        elif len(text) > 100:
            return {"value": "middle"}
        else:
            return {"value": "short"}
