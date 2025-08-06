## How to build docs

1. First install the requirements to build the docs.
   
   ```
   pip install -r ./docs/requirements.txt
   ```

2. Run sphinx apidoc to generate the documentation from docstrings in the code. 
   The official documentation is located 
   [here](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html).
    
   ```
   sphinx-apidoc -f filip -o ./docs/source/api
   ```
   
> Use `-f` to force overwrite existing files. The ``index.rst`` in `/docs/source/api/` must be manually updated if necessary
   
3. Build html by running
   ```
   sphinx-build -b html ./docs/source ./docs/build
   ```
