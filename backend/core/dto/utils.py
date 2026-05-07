from dataclasses import fields


def dto_from_model(dto_cls, model):
    if model is not None:
        return dto_cls(
            **{
                f.name: getattr(model, f.name)
                for f in fields(dto_cls)
                if hasattr(model, f.name)
            }
        )
    else:
        return None
