# git-file-keyword

Extract keywords from git history for better understanding your code files. For human and LLM.

## What is it?

We use https://github.com/axios/axios.git for example.

With a simple command:

```bash
gfk --repo ./axios --include "**/*.js" --output_csv ./output.csv
```

You can get a keywords list of all your code files, which is extracted from your git history:

<img width="953" alt="image" src="https://github.com/williamfzc/git-file-keyword/assets/13421694/bdf3668d-f6bc-488f-b722-55ff33bccc78">

These keywords can be used to guide developers/maintainers in understanding the potential functionality and history associated with these files.

And, also LLM. If you provide an openai key ...

```bash
gfk --repo ../axios --include "**/*.js" --openai_key="sk-***" --output_csv ./output.csv
```


TODO

## Motivation

TODO

## License

[Apache 2.0](LICENSE)
