# pyPassGenerator

It's a simple program that it's able of generate randoms, variables and with custom characters password.

---

Parameters
===

Order | Parameter | What doing?
--- | --- | ---
0 | *size* | You can choose how long you want to generate your password
1 | *mixVocabulary* | You choose your game of characters
2 | *repeatCharacters* | It lets or doesn't let to use characters that it already has used

size - `int`
---
You can choose how long you want to generate your password.

mixVocabulary - `String` - Default: `a`
---
You choose your game of characters.

Value | What doing?
--- | ---
*a* | All (lower/upper-case vocals, lower/upper-case consonants, numbers and specials)
*v* | Only lower-case vocals
*V* | Only upper-case vocals
*c* | Only lower-case consonants
*C* | Only upper-case consonants
*n* | Only numbers
*s* | Only specials

It's possible to use combinations, for example:

    Cn -> Only upper-case consonants and numbers.

- Example
```python
    generatePass(5, "Cn")
    return '75WT4'
```

If you want to use your own game of characters, you will type '@' at start of parameter, for example:

    @bXcD3 -> Only will be used the characters b, X, c, D and 3.

  - Example
  ```python
      generatePass(5, "@bXcD3")
      return 'X3c33'
  ```

repeatCharacters - `Boolean` - Default: `True`
---
It lets or doesn't let to use characters that it already has used.

Value|What doing?
---|---
*True* | This lets to repeat characters that it's already in passphrase.
*False* | This doesn't let to repeat characters that it's already in passphrase.
This parameter is used for generate password with characters that it isn't possible to repeat (`True`) or it's possible to repeat (`False`).
