import string

from pathlib import Path

if __name__ == '__main__':
    temt_str = Path('README_template.md').read_text()
    temp = string.Template(temt_str)
    code_files = Path('.').glob('*/main*.py')
    values = {}
    for code_file in code_files:
        values[f'code_{code_file.parent.name}_{code_file.stem}'] = (
            f'```python\n{code_file.read_text()}\n```'
        )
    values['code_wsgi_application'] = (
        f'```python\n{Path("run_wsgi/wsgi/application.py").read_text()}\n```'
    )
    result = temp.substitute(values)
    result_path = Path('README.md')
    result_path.write_text(result)
