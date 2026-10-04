# V2 documentation response fixtures

These fixtures record the exact response-example values published in TheRundown's official OpenAPI document. They are **recorded documentation examples**, not recorded production API responses. No authenticated API request was made to create them.

## Source and capture

- Source: [TheRundown OpenAPI document](https://docs.therundown.io/openapi.yaml)
- Documentation captured at UTC: `2026-10-04T15:12:43Z`
- Source document SHA-256: `edd59e33c1b0245f73a33b103d0279f60af0ad7ac88e9231ec827528a166e785`
- Source document size: `223286` bytes
- Source HTTP Last-Modified: `Sat, 19 Sep 2026 02:46:30 GMT`
- Source HTTP ETag: `W/"eXJdWnLk6OrED2FI"`

The capture time records retrieval of the documentation. The source does not establish when an underlying API response was collected, whether these examples came from an API capture, or the exact query parameters that generated them.

## Extraction and integrity

| Fixture | Source JSON Pointer | SHA-256 |
| --- | --- | --- |
| `sports_dates.json` | `/paths/~1api~1v2~1sports~1dates/get/responses/200/content/application~1json/example` | `5a43d07f02727878a1a2624229af9aaa076d508461cfe73976f7507ae8d15750` |
| `events.json` | `/paths/~1api~1v2~1sports~1{sportID}~1events~1{date}/get/responses/200/content/application~1json/example` | `803144eb0e4abc7680c2247c986c49e36169a81133679a7680f0a368c7e98ae4` |

The pointers apply to the parsed OpenAPI document; `~1` represents `/`. Each selected example is serialized as UTF-8 JSON with two-space indentation and one trailing newline. Values, fields, array ordering, timestamps, IDs, and prices are preserved. No example values were invented, projected, or redacted.

The fixtures contain response bodies only. They contain no API credentials, authorization headers, request URLs with keys, private account metadata, or affiliate 27 prices. Only the published examples were retained; SDK request serialization and validation are tested separately. These fixtures do not prove that `market_ids`, `affiliate_ids`, or `main_line` were applied by a real request.

## Endpoint documentation

- [Dates for multiple sports](https://docs.therundown.io/api-reference/generated/v2-sports/get-available-dates-for-multiple-sports)
- [Events with markets for a sport and date](https://docs.therundown.io/api-reference/generated/v2-events/get-events-with-markets-for-a-sport-and-date)

The dates example includes full timestamp strings; the SDK preserves the response as supplied. The events example uses the V2 `markets -> participants -> lines -> prices` structure.

These are examples already published by TheRundown, retained for TheRundown's own SDK tests. The [licensing and attribution documentation](https://docs.therundown.io/licensing-and-attribution) describes use of customer API data; the MIT license on a separate example-code repository does not establish permission to redistribute new API captures.
