> 🚧 **Important!** This tool is still under development, must await for further updates.

# R2MD: Rancher to Markdown [![license-badge]][license]
This is a tool that wraps version details from all PODs on Rancher to Markdown using Python utilities with Selenium Web Driver.

## Disclaimer
This tool works on Rancher version **v2.4.8** only.

## Languages
![python-language-badge] ![jupyter-language-badge]

## Workstation Setup
1. **Step 1** - install [Python][ref-1];
1. **Step 2** - install [Anaconda][ref-2];
1. **Step 3** - install web scraping dependencies:
<details open>

```terminal
conda install -c conda-forge notebook
conda install -c conda-forge jupyterlab
conda install splinter
conda install selenium
```


## Web Scraping References
- **Splinter API Reference** - https://splinter.readthedocs.io/en/latest/index.html
- **Selenium API Reference (Python)** - https://selenium-python.readthedocs.io/index.html

### Contributors
- Nádio ~ [@Devwarlt][nadio-ref]

[nadio-ref]: https://github.com/Devwarlt

[python-language-badge]: https://img.shields.io/badge/Python-3.8.3-yellow?logo=python&style=plastic
[jupyter-language-badge]: https://img.shields.io/badge/Notebook-6.0.3-yellow?logo=jupyter&style=plastic

[license-badge]: https://img.shields.io/badge/License-WTFPL-black?style=plastic
[license]: /LICENSE

[ref-1]: https://www.python.org/downloads/
[ref-2]: https://docs.anaconda.com/anaconda/install/
