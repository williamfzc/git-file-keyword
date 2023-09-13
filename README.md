# git-file-keyword

> Auto-generate Code File Descriptions with Git History and LLM.

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
gfk --repo ../axios --include "**/*.js" --output_csv ./output.csv --openai_key="sk-***"
```

![image](https://github.com/williamfzc/git-file-keyword/assets/13421694/a63ac735-4ec5-48eb-94cb-d1ed70879c36)

You will see the human-readable descriptions for every source files. For example:

```text
lib/core/Axios.js

A core file that handles Axios configuration, interceptors, and request defaults.
```

We used LLM as a keyword parser to analyze, organize, and summarize the functionality of each file, and present it in a human-readable format. 

## Usage

```commandline
pip3 install git-file-keyword
```

### In terminal

```commandline
gfk --repo ../axios --include "**/*.js" --output_csv ./output.csv --openai_key="sk-***"
```

Of course, there will be a significant number of meaningless phrases in the commit records. 
While we have utilized extensive existing stop-word libraries to address some of them, the same words may carry different meanings in different repositories, and there is no universal solution.

So you can simply exclude them by adding `your_stopwords.txt` file:

```text
stop_word1
stop_word2
stop_word3
```

And add it to your command:

```commandline
--stopword_txt your_stopwords.txt
```

### As a lib

We provided some examples:

- [example/diff.py](example/diff.py): Get diff files and extract what they actually mean
- [example/stopword_extractor.py](example/stopword_extractor.py): Extract global keywords
- [git_file_keyword/cli/__init__.py](git_file_keyword/cli/__init__.py): Our cmd client

## Motivation

- Automatic maintenance of an always up-to-date document.
- By extracting sufficient business context from the git history, git-file-keyword allows developers and LLMs to quickly understand the meaning behind each code file at a lower cost.
- Enable clear positive feedback loops within the team through the use of commit messages.

## How it works?

gfk consists of 3 layers:

- Word extractor: extract words from git history and related platforms like JIRA
- Keyword finder: find the keywords from words
- LLM connector: prompt and communication with llm

## Contribution

Issues and PRs are always welcome :)

## License

[Apache 2.0](LICENSE)
