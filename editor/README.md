```
fetch(
      `https://en.wikipedia.org/wiki/Timeline_of_World_War_II_(${state.year})`,
      {
        mode: 'no-cors',
        headers: {
          accept: 'text/html',
          origin: "https://en.wikipedia.org"
        },
      }
    )
```