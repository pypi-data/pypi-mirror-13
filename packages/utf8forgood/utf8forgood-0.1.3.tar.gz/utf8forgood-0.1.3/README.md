utf8forgood
-----------

**Tired of Python's `UnicodeDeocodeError, ascii codec can't decode?`**

Here's how to fix it, once and for all.

1. `$ pip install utf8forgood`
2. in your main program, add

    ```
    import utf8forgood
    ```
If you like it, make the change permanent in your sitecustomize.py:

    ```
    # /path/to/site-packages/sitecustomize.py
    import utf8forgood
    ```

To find the path to `sitecustomize.py`, run `python -m site` or read up on
the [site-specific configuration hook][8].

Why?
----

In general to the above, the fastest remedy is probably trying out the following, in this order:

1. Use `PYTONIOENCODING=UTF-8 python /path/to/program.py`
2. Use the [`sys.setdefaultencoding`][1] hack. That is, unless you care [what others say][2]
3. Write your own import function to [convert data][3] appropriately, which is generally the [recommended way][4].

After [much consideration][7] and trying option 3 I finally concluded that option 2
is the straight forward way and usually [just does what you want][5], on the off-chance of [getting yourself in trouble][6].

  [1]: http://stackoverflow.com/a/17628350/890242
  [2]: http://stackoverflow.com/questions/28657010/dangers-of-sys-setdefaultencodingutf-8
  [3]: http://stackoverflow.com/a/28760303/890242
  [4]: http://stackoverflow.com/a/34378962/890242
  [5]: http://stackoverflow.com/a/29558302/890242
  [6]: http://stackoverflow.com/a/29561747/890242
  [7]: http://stackoverflow.com/a/27745947/890242
  [8]: https://docs.python.org/2/library/site.html
