## How to build docs

1. First install the requirements to build the docs.
   
   ```
   pip install -r ./docs/requirements.txt
   ```

2. Run sphinx apidoc to generate the documentation from docstings in the code. 
   The official documentation is located 
   [here](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html).
    
   ```
   sphinx-apidoc filip -o ./docs/source/api --tocfile index
   ```
   
3. Build html by running
   ```
   sphinx-build -b html ./docs/source ./docs/build
   ```