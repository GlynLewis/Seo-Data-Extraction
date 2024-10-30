
Instead of ‘login’ and ‘password’ use your credentials from https://app.dataforseo.com/api-dashboard

            

from client import RestClient
# You can download this file from here https://api.dataforseo.com/v3/_examples/python/_python_Client.zip
client = RestClient("login", "password")
post_data = dict()
# simple way to set a task
post_data[len(post_data)] = dict(
    target="backlinko.com",
    exclude_internal_backlinks=True,
    filters=["referring_domains", ">", 10],
    backlinks_filters=["dofollow", "=", True],
    order_by=["rank,desc"],
    limit=5
)
# POST /v3/backlinks/referring_domains/live
# the full list of possible parameters is available in documentation
response = client.post("/v3/backlinks/referring_domains/live", post_data)
# you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
if response["status_code"] == 20000:
    print(response)
    # do something with result
else:
    print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


        

The above command returns JSON structured like this:


{
  "version": "0.1.20230825",
  "status_code": 20000,
  "status_message": "Ok.",
  "time": "0.8296 sec.",
  "cost": 0.02015,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [
    {
      "id": "09291844-1535-0273-0000-a8b98c0b9eab",
      "status_code": 20000,
      "status_message": "Ok.",
      "time": "0.7705 sec.",
      "cost": 0.02015,
      "result_count": 1,
      "path": [
        "v3",
        "backlinks",
        "referring_domains",
        "live"
      ],
      "data": {
        "api": "backlinks",
        "function": "referring_domains",
        "target": "backlinko.com",
        "limit": 5,
        "order_by": [
          "rank,desc"
        ],
        "exclude_internal_backlinks": true,
        "backlinks_filters": [
          "dofollow",
          "=",
          true
        ],
        "filters": [
          "backlinks",
          ">",
          100
        ]
      },
      "result": [
        {
          "target": "backlinko.com",
          "total_count": 131,
          "items_count": 5,
          "items": [
            {
              "type": "backlinks_referring_domain",
              "domain": "menaccessories.net",
              "rank": 302,
              "backlinks": 9864,
              "first_seen": "2021-10-16 16:46:16 +00:00",
              "lost_date": null,
              "backlinks_spam_score": 0,
              "broken_backlinks": 0,
              "broken_pages": 0,
              "referring_domains": 1,
              "referring_domains_nofollow": 0,
              "referring_main_domains": 1,
              "referring_main_domains_nofollow": 0,
              "referring_ips": 1,
              "referring_subnets": 1,
              "referring_pages": 9864,
              "referring_links_tld": {
                "net": 9864
              },
              "referring_links_types": {
                "anchor": 9864
              },
              "referring_links_attributes": null,
              "referring_links_platform_types": {
                "blogs": 9864,
                "cms": 9864,
                "ecommerce": 9840
              },
              "referring_links_semantic_locations": {
                "": 9864
              },
              "referring_links_countries": {
                "": 6392,
                "US": 3472
              },
              "referring_pages_nofollow": 0
            },
            {
              "type": "backlinks_referring_domain",
              "domain": "semrush.com",
              "rank": 299,
              "backlinks": 238,
              "first_seen": "2019-09-17 05:41:24 +00:00",
              "lost_date": null,
              "backlinks_spam_score": 0,
              "broken_backlinks": 0,
              "broken_pages": 0,
              "referring_domains": 7,
              "referring_domains_nofollow": 0,
              "referring_main_domains": 1,
              "referring_main_domains_nofollow": 0,
              "referring_ips": 1,
              "referring_subnets": 1,
              "referring_pages": 204,
              "referring_links_tld": {
                "com": 204
              },
              "referring_links_types": {
                "anchor": 201,
                "image": 3
              },
              "referring_links_attributes": {
                "noopener": 1,
                "noreferrer": 1
              },
              "referring_links_platform_types": {
                "organization": 204,
                "blogs": 1,
                "news": 1
              },
              "referring_links_semantic_locations": {
                "article": 197,
                "figcaption": 3,
                "figure": 3,
                "main": 1
              },
              "referring_links_countries": {
                "US": 62,
                "ES": 60,
                "DE": 39,
                "IT": 14,
                "FR": 13,
                "PT": 12,
                "": 4
              },
              "referring_pages_nofollow": 0
            },
            {
              "type": "backlinks_referring_domain",
              "domain": "alexamaster.net",
              "rank": 290,
              "backlinks": 3278,
              "first_seen": "2023-06-30 16:23:26 +00:00",
              "lost_date": null,
              "backlinks_spam_score": 0,
              "broken_backlinks": 0,
              "broken_pages": 0,
              "referring_domains": 1,
              "referring_domains_nofollow": 0,
              "referring_main_domains": 1,
              "referring_main_domains_nofollow": 0,
              "referring_ips": 1,
              "referring_subnets": 1,
              "referring_pages": 3278,
              "referring_links_tld": {
                "net": 3278
              },
              "referring_links_types": {
                "anchor": 3278
              },
              "referring_links_attributes": null,
              "referring_links_platform_types": {
                "unknown": 3278
              },
              "referring_links_semantic_locations": {
                "section": 3278
              },
              "referring_links_countries": {
                "": 3278
              },
              "referring_pages_nofollow": 0
            },
            {
              "type": "backlinks_referring_domain",
              "domain": "edynamique.com",
              "rank": 286,
              "backlinks": 28356,
              "first_seen": "2020-02-27 16:30:49 +00:00",
              "lost_date": null,
              "backlinks_spam_score": 14,
              "broken_backlinks": 0,
              "broken_pages": 0,
              "referring_domains": 1,
              "referring_domains_nofollow": 0,
              "referring_main_domains": 1,
              "referring_main_domains_nofollow": 0,
              "referring_ips": 1,
              "referring_subnets": 1,
              "referring_pages": 13030,
              "referring_links_tld": {
                "com": 13030
              },
              "referring_links_types": {
                "anchor": 12457,
                "image": 573
              },
              "referring_links_attributes": {
                "noopener": 12457,
                "noreferrer": 997
              },
              "referring_links_platform_types": {
                "blogs": 13030,
                "news": 13030
              },
              "referring_links_semantic_locations": {
                "": 13030
              },
              "referring_links_countries": {
                "CA": 7085,
                "": 5945
              },
              "referring_pages_nofollow": 0
            },
            {
              "type": "backlinks_referring_domain",
              "domain": "gloria-project.eu",
              "rank": 279,
              "backlinks": 1948,
              "first_seen": "2021-12-23 14:01:45 +00:00",
              "lost_date": null,
              "backlinks_spam_score": 0,
              "broken_backlinks": 0,
              "broken_pages": 0,
              "referring_domains": 2,
              "referring_domains_nofollow": 0,
              "referring_main_domains": 1,
              "referring_main_domains_nofollow": 0,
              "referring_ips": 2,
              "referring_subnets": 2,
              "referring_pages": 1948,
              "referring_links_tld": {
                "eu": 1948
              },
              "referring_links_types": {
                "anchor": 1948
              },
              "referring_links_attributes": {
                "noopener": 1839,
                "noreferrer": 541
              },
              "referring_links_platform_types": {
                "blogs": 1948,
                "cms": 1948,
                "organization": 1948
              },
              "referring_links_semantic_locations": {
                "article": 1948
              },
              "referring_links_countries": {
                "FR": 1855,
                "": 76,
                "UA": 17
              },
              "referring_pages_nofollow": 0
            }
          ]
        }
      ]
    }
  ]
}

POST https://api.dataforseo.com/v3/backlinks/referring_domains/live
 Your account will be charged for each request.
The cost can be calculated on the Pricing page.
All POST data should be sent in the JSON format (UTF-8 encoding). The task setting is done using the POST method. When setting a task, you should send all task parameters in the task array of the generic POST array.

Description of the fields for setting a task:

Field name	Type	Description
target	string	domain, subdomain or webpage to get referring domains for
required field
a domain or a subdomain should be specified without https:// and www.
a page should be specified with absolute URL (including http:// or https://)
limit	integer	the maximum number of returned domains
optional field
default value: 100
maximum value: 1000
offset	integer	offset in the results array of returned domains
optional field
default value: 0
if you specify the 10 value, the first ten domains in the results array will be omitted and the data will be provided for the successive pages
internal_list_limit	integer	maximum number of elements within internal arrays
optional field
you can use this field to limit the number of elements within the following arrays:
referring_links_tld
referring_links_types
referring_links_attributes
referring_links_platform_types
referring_links_semantic_locations
default value: 10
maximum value: 1000

backlinks_status_type	string	set what backlinks to return and count
optional field
you can use this field to choose what backlinks will be returned and used for aggregated metrics for your target;
possible values:
all – all backlinks will be returned and counted;
live – backlinks found during the last check will be returned and counted;
lost – lost backlinks will be returned and counted;
default value: live

filters	array	array of results filtering parameters
optional field
you can add several filters at once (8 filters maximum)
you should set a logical operator and, or between the conditions
the following operators are supported:
regex, not_regex, =, <>, in, not_in, like, not_like
you can use the % operator with like and not_like to match any string of zero or more characters
example:
["referring_pages",">","1"]
[["referring_pages",">","2"],
"and",
["backlinks",">","10"]]

[["first_seen",">","2017-10-23 11:31:45 +00:00"],
"and",
[["domain","like","%dataforseo.com%"],"or",["referring_domains",">","10"]]]

The full list of possible filters is available here.

order_by	array	results sorting rules
optional field
you can use the same values as in the filters array to sort the results
possible sorting types:
asc – results will be sorted in the ascending order
desc – results will be sorted in the descending order
you should use a comma to set up a sorting type
example:
["backlinks,desc"]
note that you can set no more than three sorting rules in a single request
you should use a comma to separate several sorting rules
example:
["backlinks,desc","rank,asc"]
backlinks_filters	array	filter the backlinks of your target
optional field
you can use this field to filter the initial backlinks that will be included in the dataset for aggregated metrics for your target
you can filter the backlinks by all fields available in the response of this endpoint
using this parameter, you can include only dofollow backlinks in the response and create a flexible backlinks dataset to calculate the metrics for
example:
"backlinks_filters": ["dofollow", "=", true]
include_subdomains	boolean	indicates if the subdomains of the target will be included in the search
optional field
if set to false, the subdomains will be ignored
default value: true
include_indirect_links	boolean	indicates if indirect links to the target will be included in the results
optional field
if set to true, the results will include data on indirect links pointing to a page that either redirects to the target, or points to a canonical page
if set to false, indirect links will be ignored
default value: true
exclude_internal_backlinks	boolean	indicates whether the backlinks from subdomains of the target are excluded
optional field
if set to false, the backlinks from subdomains of the target will be ommited and you won’t receive the same domain in the response;
default value: true
tag	string	user-defined task identifier
optional field
the character limit is 255
you can use this parameter to identify the task and match it with the result
you will find the specified tag value in the data object of the response
‌‌‌‌‌‌
As a response of the API server, you will receive JSON-encoded data containing a tasks array with the information specific to the set tasks.

Description of the fields in the results array:

Field name	Type	Description
version	string	the current version of the API
status_code	integer	general status code
you can find the full list of the response codes here
Note: we strongly recommend designing a necessary system for handling related exceptional or error conditions
status_message	string	general informational message
you can find the full list of general informational messages here
time	string	execution time, seconds
cost	float	total tasks cost, USD
tasks_count	integer	the number of tasks in the tasks array
tasks_error	integer	the number of tasks in the tasks array returned with an error
tasks	array	array of tasks
        id	string	task identifier
unique task identifier in our system in the UUID format
        status_code	integer	status code of the task
generated by DataForSEO; can be within the following range: 10000-60000
you can find the full list of the response codes here
        status_message	string	informational message of the task
you can find the full list of general informational messages here
        time	string	execution time, seconds
        cost	float	cost of the task, USD
        result_count	integer	number of elements in the result array
        path	array	URL path
        data	object	contains the same parameters that you specified in the POST request
        result	array	array of results
            target	string	target in a POST array
            total_count	integer	total number of relevant items in the database
total number of main domains referring to your target;
example.com and blog.example.com are counted as one referring domain
            items_count	integer	number of items in the items array
            items	array	items array
                type	string	type of element = ‘backlinks_referring_domain’
                domain	string	referring domain
                rank	integer	domain rank
rank volume that a referring website passes to the target
rank is calculated based on the method for node ranking in a linked database – a principle used in the original Google PageRank algorithm
learn more about the metric and how it is calculated in this help center article
                backlinks	integer	indicates the number of backlinks pointing to the target
                first_seen	string	date and time when our crawler found the backlink for the first time
in the UTC format: “yyyy-mm-dd hh-mm-ss +00:00”
example:
2019-11-15 12:57:46 +00:00
                lost_date	string	date and time when the last backlink from this domain was lost
indicates the date and time when our crawler visited the page and it responded with 4xx or 5xx status code or the last backlink was removed
in the UTC format: “yyyy-mm-dd hh-mm-ss +00:00”
example:
2017-01-24 13:20:59 +00:00
                backlinks_spam_score	integer	average spam score of all backlinks pointing to the domain
learn more about how the metric is calculated on this help center page
                broken_backlinks	integer	number of broken backlinks
number of broken backlinks pointing to the domain
                broken_pages	integer	number of broken pages
number of pages that respond with 4xx or 5xx status codes where backlinks are pointing to
                referring_domains	integer	indicates the number of referring domains
note that we calculate main domains (root domains, like example.com) and their subdomains (e.g. blog.example.com) separately for this metric
                referring_domains_nofollow	integer	number of domains pointing at least one nofollow link to the target
                referring_main_domains	integer	indicates the number of referring main domains
the number of primary (root) domains referring to your target
                referring_main_domains_nofollow	integer	number of main domains pointing at least one nofollow link to the target
                referring ips	integer	number of referring IP addresses
number of IP addresses pointing to this page
                referring subnets	integer	number of referring subnetworks
                referring_pages	integer	indicates the number of pages pointing to the target specified
                referring_links_tld	object	top-level domains of the referring links
contains top level domains and referring link count per each
                referring_links_types	object	types of referring links
indicates the types of the referring links and link count per each type
possible values:
anchor, image, link, meta, canonical, alternate, redirect
                referring_links_attributes	object	link attributes of the referring links
indicates link attributes of the referring links and link count per each attribute
                referring_links_platform_types	object	types of referring platforms
indicates referring platform types and link count per each platform
                referring_links_semantic_locations	object	semantic locations of the referring links
indicates semantic elements in HTML where the referring links are located and the link count per each semantic location
you can get the full list of semantic elements here
examples:
article, section, summary

                referring_links_countries	object	ISO country codes of the referring links
indicates ISO country codes of the domains where the referring links are located and the link count per each country
                referring_pages_nofollow	integer	number of referring pages pointing at least one nofollow link to the target
