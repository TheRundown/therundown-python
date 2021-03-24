### General Idea

There will be 2 folders, `api` and `resources`. `api` has all the methods / functions for calling the REST API. For now, there are multiple design alternatives in the `api-*` folders. `resources` has all the classes that get created and returned from the functions in the `api` folder. The classes in `resources` model the structure of the objects returned from the REST API.

API calls are made easier by allowing the user to create an instance of the `Config` class which stores information such as their API key, timezone, odds type preference, sportsbooks of interest. Timezone, odds type, and sportsbooks are only relevant if we decide to implement extra functionality. Calls to endpoints requiring a date can then utilize a timezone-aware datetime object.

The created resources should have cleaned and munged data wherever possible, including correct timezone and odds types. So all the data processing will happen between the API call and the returned objects. Parsing the response into defined resources will make it easier to build on top of if there are new features.

### API class alternatives

I defined 2 alternatives in `api-methods` and `api-subclasses`. `api-methods` just has all REST endpoints as methods. `api-subclasses` splits the endpoints up into groups. Each endpoint could also be its own class. 2 examples are shown in `api-classes`.

#### Example calls

`api-methods`:

```python
r = rundown(rapidapi_key='foo', timezone='PST', affiliates=['Bovada', 'Pinnacle'])
e = r.events_by_date(sport_id=1, date_=date.today())
sbs = r.affiliates()
```

`api-subclasses`:

```python
e = Events(rapidapi_key='foo', timezone='PST', affiliates=['Bovada', 'Pinnacle'])
sb = Sportsbook(rapidapi_key='foo')
e_list = e.by_date(sport_id=1, date_=date.today())
sbs = sb.affiliates()
```

Each endpoint as its own class (2 example classes shown in `api-classes`):

```python
config = Config(rapidapi_key='foo', timezone='PST', affiliates=['Bovada', 'Pinnacle'])
e = EventsByDate(sport_id=1, date_=date.today(), **config) # returns resources.Events
a = Affiliates(**config) # returns list of resources.Affiliate
```

### Optimizations

- dates with timezone
- different odds types
- filter by sportsbook
- Static classes storing affiliates and teams for each sport to avoid extra API calls
- allow for multiple calls to REST API in one function call
  - Events by date range
  - Events by multiple sports...
