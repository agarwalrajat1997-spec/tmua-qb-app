from economics_author import *
import importlib

if __name__ == '__main__':
    for module in ['econ_intro','econ_micro','econ_macro','econ_global']:
        try:
            importlib.import_module(module).build()
        except ModuleNotFoundError as exc:
            if exc.name != module: raise
    import econ_variants
    econ_variants.enrich()
    save()
    print({topic:len(rows) for topic,rows in QUESTIONS.items()})
