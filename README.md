---
title: ReviewGPT
emoji: 🦀
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 3.23.0
app_file: reviewGPT.py
pinned: true
license: mit
---

# ReviewGPT

Researchers need to read a large amount of literature every day to keep up with the latest research progress, but the fragmentation of research results is even worse than that of Linux distributions, which slows down research work to some extent. This project aims to use ChatGPT to perform some scientific literature retrieval and work during the reading process, so that related work can be faster and more efficient.

## Demo

[Demo](https://huggingface.co/spaces/SilenWang/ReviewGPT) available on Huggingface, an OpenAI API Key is required

- Screen:

![demo](img/screen.png)

- Summarise:

![demo](img/summarise.png)


## ToDo

- Frontend:
  + [x] A basic app but usable app
  + [x] Setting key from frontend
  + [ ] Add a download button for raw parsing data(json) 
  + [x] Implementation of content summarise function
  + [ ] The About page
  + [ ] Add usage instructions
  + [ ] Paper Reading Page
- Backend: 
  + [x] Call the chatGPT API for content summarization
  + [x] Call the chatGPT API for literature content access judgment (for meta-analysis)
  + [x] Call the biopython API to obtain literature bibliographic information and abstracts from PUBMED
  + [ ] Save and package raw parsing data
    * ~~Data security issues here, necessary to understand whether the returned id will cause Key leakage ~~
  + [ ] ~~Add multiple repetitions of content access judgment (check whether the result is stable)~~
  + [x] RIS file upload and parsing support
  + [ ] Support for models other than chatGPT
    + [ ] chatGLM
    + [ ] moss
    + [ ] LLaMA
  + [x] Add the function of reading single paper
  + [ ] Add APIs for existing feature
- Reference learning:
  + [ ] Learn the content of[ResearchGPT](https://github.com/mukulpatnaik/researchgpt) and add similar function
  + [ ] Learn the content of[chatPaper](https://github.com/kaixindelele/ChatPaper) and add similar function
  + [ ] ~~Try build something like [chatPDF](https://www.chatpdf.com/)~~
- Others:
  - [x] Enhlish README
  - [ ] Dockfile for container building
  - [x] A HuggingFace demo
  - [ ] Add error handling for network tasks, following the example of [chatPaper](https://github.com/kaixindelele/ChatPaper)

## Code Interpretation

- According to chatGPT, the implementation of ResearchGPT is as follows:
  + Convert file contents by page into text
  + Call `text-embedding-ada-002` for text embedding matrix calculation
  + Convert the question into a matrix and calculate the similarity with the matrix of each page
  + Send the top 3 pages with the highest similarity to the proposed question to the chatGPT interface for literature interpretation

## Problems

- This project was initially developed using Pynecone, but encountered several problems that affected its use/appearance, so it was finally switched to Gradio.
  + pynecone continues to occupy the CPU after startup.
  + Currently, the file upload function is not very user-friendly, and you must use buttons or other content to trigger the upload (I have not found how to implement drag and drop upload).
  + After uploading the file, performing other operations will cause the displayed file name to be lost.
