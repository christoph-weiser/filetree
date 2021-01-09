## Filetree - Compare File and Directory structures


### commandline example
Filetree can be used directly from the commandline using the script
provided in scripts folder. 

```
filetree dir_a dirb
```

### script example
Alternatively it can be used in customs python scripts using 
Filetree and/or Dirtree objects.

```python

from filetree import Filetree, compare_set

fta = Filetree("./dir_a")
ftb = Filetree("./dir_b")

result = compare_set(fta, ftb)
```



