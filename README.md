# TheRundown Python SDK

## API v2

The small synchronous v2 client currently supports two methods:

| Method | Documented endpoint |
|---|---|
| `list_sports_dates(sport_ids=None)` | `GET /api/v2/sports/dates` |
| `get_events(sport_id, event_date, *, market_ids=None, affiliate_ids=None, main_line=None)` | `GET /api/v2/sports/{sportID}/events/{date}` |

Install from this repository with `pip install .`. Set `THERUNDOWN_API_KEY` in
your private environment, or pass `api_key` to the constructor. The base URL is
`https://therundown.io/api/v2`; authentication uses the `X-TheRundown-Key` header.

```python
from rundown import TheRundownClient

with TheRundownClient() as client:
    sports_dates = client.list_sports_dates(sport_ids=[1, 2])
    response = client.get_events(
        1,
        "2026-10-03",
        market_ids=[41, 42, 43],
        affiliate_ids=[3, 19],
        main_line=True,
    )
    for event in response["events"]:
        print(event["event_id"])
```

Filters accept integer sequences or comma-separated strings. `None` omits a
filter; empty filters are rejected to avoid unintentionally broad requests.
`main_line=True` also excludes closed prices. `affiliate_ids=[0]` requests
scores/status without markets. Requests allow at most 12 market IDs. Omitted
filters retain API defaults; date boundaries use the API's default UTC day.

Both methods return the complete JSON dictionary unchanged, preserving string
IDs, timestamps, odds and sentinel values. The default timeout is 30 seconds,
configurable with `timeout=`. HTTP errors raise `requests.HTTPError`, and timeout
or connection errors use the corresponding requests exceptions. No automatic
retries are made. `client.last_response` exposes the latest response, including
error payloads, `Retry-After`, usage and data-delay headers. Redirects are rejected
so the API-key header is not sent to redirect targets. Use the context manager or
call `close()` to release connections.

Contracts were checked against the live official documentation before adding
these methods:

- [Sports dates](https://docs.therundown.io/api-reference/generated/v2-sports/get-available-dates-for-multiple-sports)
- [Sport/date events](https://docs.therundown.io/api-reference/generated/v2-events/get-events-with-markets-for-a-sport-and-date)
- [Authentication](https://docs.therundown.io/authentication)
- [Errors](https://docs.therundown.io/errors)

Tests use recorded fixtures and mocked HTTP; they do not call production. The
existing v1 client is still available from `rundown.rundown`.

## Original v1 design notes

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
