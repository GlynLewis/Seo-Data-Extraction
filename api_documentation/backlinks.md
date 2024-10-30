 returned; the number of duplicate backlinks from the referring page will be indicated in the links_count field.

Instead of ‘login’ and ‘password’ use your credentials from https://app.dataforseo.com/api-dashboard

            

from client import RestClient
# You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
client = RestClient("login", "password")
post_data = dict()
# simple way to set a task
post_data[len(post_data)] = dict(
    target="forbes.com",
    limit=5,
    mode="as_is",
    filters=["dofollow", "=", True]
)
# POST /v3/backlinks/backlinks/live
response = client.post("/v3/backlinks/backlinks/live", post_data)
# you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
if response["status_code"] == 20000:
    print(response)
    # do something with result
else:
    print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


        

The above command returns JSON structured like this:


{
    "version": "0.1.20221214",
    "status_code": 20000,
    "status_message": "Ok.",
    "time": "2.1211 sec.",
    "cost": 0.02015,
    "tasks_count": 1,
    "tasks_error": 0,
    "tasks": [
        {
            "id": "04301435-1535-0269-0000-f29dcb15157f",
            "status_code": 20000,
            "status_message": "Ok.",
            "time": "2.0475 sec.",
            "cost": 0.02015,
            "result_count": 1,
            "path": [
                "v3",
                "backlinks",
                "backlinks",
                "live"
            ],
            "data": {
                "api": "backlinks",
                "function": "backlinks",
                "target": "forbes.com",
                "mode": "as_is",
                "filters": [
                    "dofollow",
                    "=",
                    true
                ],
                "limit": 5
            },
            "result": [
                {
                    "target": "forbes.com",
                    "mode": "as_is",
                    "custom_mode": null,
                    "total_count": 42671699,
                    "items_count": 5,
                    "items": [
                        {
                            "type": "backlink",
                            "domain_from": "www.opencart.com",
                            "url_from": "https://www.opencart.com/",
                            "url_from_https": true,
                            "domain_to": "www.forbes.com",
                            "url_to": "http://www.forbes.com/sites/brentgleeson/2014/09/05/3-steps-to-launch-your-first-ecommerce-website/",
                            "url_to_https": false,
                            "tld_from": "com",
                            "is_new": false,
                            "is_lost": false,
                            "backlink_spam_score": 0,
                            "rank": 862,
                            "page_from_rank": 1000,
                            "domain_from_rank": 716,
                            "domain_from_platform_type": [
                                "unknown"
                            ],
                            "domain_from_is_ip": false,
                            "domain_from_ip": "104.20.14.19",
                            "domain_from_country": "WW",
                            "page_from_external_links": 22,
                            "page_from_internal_links": 17,
                            "page_from_size": 21655,
                            "page_from_encoding": "utf-8",
                            "page_from_language": "en",
                            "page_from_title": "OpenCart - Open Source Shopping Cart Solution",
                            "page_from_status_code": 200,
                            "first_seen": "2019-01-21 18:17:01 +00:00",
                            "prev_seen": "2023-02-10 16:15:27 +00:00",
                            "last_seen": "2023-04-11 16:16:52 +00:00",
                            "item_type": "image",
                            "attributes": null,
                            "dofollow": true,
                            "original": false,
                            "alt": "Forbes",
                            "image_url": "https://www.opencart.com/application/view/image/home/featured/forbes.png",
                            "anchor": null,
                            "text_pre": null,
                            "text_post": null,
                            "semantic_location": null,
                            "links_count": 1,
                            "group_count": 0,
                            "is_broken": false,
                            "url_to_status_code": 301,
                            "url_to_spam_score": 0,
                            "url_to_redirect_target": "https://www.forbes.com/sites/brentgleeson/2014/09/05/3-steps-to-launch-your-first-ecommerce-website/"
                            "ranked_keywords_info": {
                                "page_from_keywords_count_top_3": 26,
                                "page_from_keywords_count_top_10": 62,
                                "page_from_keywords_count_top_100": 2034
                            },
                            "is_indirect_link": true,
                            "indirect_link_path": [
                                {
                                    "type": "redirect",
                                    "status_code": 302,
                                    "url": "https://goo.gl/0fV3mB"
                                }
                            ]
                        },
                        {
                            "type": "backlink",
                            "domain_from": "www.parsintl.com",
                            "url_from": "https://www.parsintl.com/publications/forbes/",
                            "url_from_https": true,
                            "domain_to": "www.forbes.com",
                            "url_to": "https://www.forbes.com/",
                            "url_to_https": true,
                            "tld_from": "com",
                            "is_new": false,
                            "is_lost": false,
                            "backlink_spam_score": 0,
                            "rank": 827,
                            "page_from_rank": 897,
                            "domain_from_rank": 635,
                            "domain_from_platform_type": [
                                "cms",
                                "blogs"
                            ],
                            "domain_from_is_ip": false,
                            "domain_from_ip": "35.232.48.95",
                            "domain_from_country": null,
                            "page_from_external_links": 2,
                            "page_from_internal_links": 23,
                            "page_from_size": 346761,
                            "page_from_encoding": "utf-8",
                            "page_from_language": "en",
                            "page_from_title": "Forbes - PARS",
                            "page_from_status_code": 200,
                            "first_seen": "2022-04-01 00:45:19 +00:00",
                            "prev_seen": "2022-12-15 15:08:15 +00:00",
                            "last_seen": "2023-01-23 10:56:18 +00:00",
                            "item_type": "anchor",
                            "attributes": null,
                            "dofollow": true,
                            "original": false,
                            "alt": null,
                            "image_url": null,
                            "anchor": "forbes.com",
                            "text_pre": null,
                            "text_post": null,
                            "semantic_location": "section",
                            "links_count": 1,
                            "group_count": 0,
                            "is_broken": false,
                            "url_to_status_code": 200,
                            "url_to_spam_score": 5,
                            "url_to_redirect_target": null
                            "ranked_keywords_info": {
                                "page_from_keywords_count_top_3": 28,
                                "page_from_keywords_count_top_10": 60,
                                "page_from_keywords_count_top_100": 1979
                            },
                            "is_indirect_link": false,
                            "indirect_link_path": null
                        },
                        {
                            "type": "backlink",
                            "domain_from": "www.google.com",
                            "url_from": "https://www.google.com/recaptcha/about/",
                            "url_from_https": true,
                            "domain_to": "www.forbes.com",
                            "url_to": "https://www.forbes.com/sites/googlecloud/2021/04/01/bot-attacks-are-the-biggest-online-risk-you-havent-addressed/?sh=4cec49d46dda/",
                            "url_to_https": true,
                            "tld_from": "com",
                            "is_new": false,
                            "is_lost": false,
                            "backlink_spam_score": 0,
                            "rank": 765,
                            "page_from_rank": 948,
                            "domain_from_rank": 970,
                            "domain_from_platform_type": [
                                "unknown"
                            ],
                            "domain_from_is_ip": false,
                            "domain_from_ip": "142.250.185.164",
                            "domain_from_country": "US",
                            "page_from_external_links": 19,
                            "page_from_internal_links": 6,
                            "page_from_size": 80722,
                            "page_from_encoding": "utf-8",
                            "page_from_language": "en",
                            "page_from_title": "reCAPTCHA",
                            "page_from_status_code": 200,
                            "first_seen": "2021-08-06 17:27:22 +00:00",
                            "prev_seen": "2022-07-03 15:43:19 +00:00",
                            "last_seen": "2023-02-04 18:12:36 +00:00",
                            "item_type": "image",
                            "attributes": null,
                            "dofollow": true,
                            "original": false,
                            "alt": "Forbes: Bot Attacks Are The Biggest Online Risk You Haven’t Addressed; See How reCAPTCHA Enterprise Can Help",
                            "image_url": "https://www.google.com/recaptcha/about/images/table-link.svg",
                            "anchor": "Forbes: Bot Attacks Are The Biggest Online Risk You Haven’t Addressed; See How reCAPTCHA Enterprise Can Help",
                            "text_pre": "}",
                            "text_post": "@media (max-width: 718px) {",
                            "semantic_location": null,
                            "links_count": 1,
                            "group_count": 0,
                            "is_broken": false,
                            "url_to_status_code": 200,
                            "url_to_spam_score": 0,
                            "url_to_redirect_target": null
                            "ranked_keywords_info": {
                                "page_from_keywords_count_top_3": 0,
                                "page_from_keywords_count_top_10": 2,
                                "page_from_keywords_count_top_100": 38
                            },
                            "is_indirect_link": false,
                            "indirect_link_path": null
                        },
                        {
                            "type": "backlink",
                            "domain_from": "www.forbesmedia.com",
                            "url_from": "http://www.forbesmedia.com/",
                            "url_from_https": false,
                            "domain_to": "www.forbes.com",
                            "url_to": "https://www.forbes.com/forbes-media/",
                            "url_to_https": true,
                            "tld_from": "com",
                            "is_new": false,
                            "is_lost": false,
                            "backlink_spam_score": 0,
                            "rank": 745,
                            "page_from_rank": 756,
                            "domain_from_rank": 566,
                            "domain_from_platform_type": null,
                            "domain_from_is_ip": false,
                            "domain_from_ip": "151.101.0.204",
                            "domain_from_country": null,
                            "page_from_external_links": 0,
                            "page_from_internal_links": 0,
                            "page_from_size": 0,
                            "page_from_encoding": null,
                            "page_from_language": null,
                            "page_from_title": null,
                            "page_from_status_code": 301,
                            "first_seen": "2021-12-17 16:30:59 +00:00",
                            "prev_seen": "2023-01-18 21:43:57 +00:00",
                            "last_seen": "2023-03-19 21:44:50 +00:00",
                            "item_type": "redirect",
                            "attributes": null,
                            "dofollow": true,
                            "original": false,
                            "alt": null,
                            "image_url": null,
                            "anchor": null,
                            "text_pre": null,
                            "text_post": null,
                            "semantic_location": null,
                            "links_count": 1,
                            "group_count": 0,
                            "is_broken": false,
                            "url_to_status_code": 301,
                            "url_to_spam_score": 0,
                            "url_to_redirect_target": "https://www.forbes.com/connect/"
                            "ranked_keywords_info": {
                                "page_from_keywords_count_top_3": 0,
                                "page_from_keywords_count_top_10": 0,
                                "page_from_keywords_count_top_100": 0
                            },
                            "is_indirect_link": false,
                            "indirect_link_path": null
                        },
                        {
                            "type": "backlink",
                            "domain_from": "www.marketwatch.com",
                            "url_from": "https://www.marketwatch.com/story/from-6000-to-67-billion-warren-buffetts-wealth-through-the-ages-2015-08-17",
                            "url_from_https": true,
                            "domain_to": "www.forbes.com",
                            "url_to": "http://www.forbes.com/pictures/gfgl45gfgf/warren-buffett/?ss=forbes400",
                            "url_to_https": false,
                            "tld_from": "com",
                            "is_new": false,
                            "is_lost": false,
                            "backlink_spam_score": 0,
                            "rank": 666,
                            "page_from_rank": 879,
                            "domain_from_rank": 688,
                            "domain_from_platform_type": [
                                "news"
                            ],
                            "domain_from_is_ip": false,
                            "domain_from_ip": "13.32.121.54",
                            "domain_from_country": "US",
                            "page_from_external_links": 42,
                            "page_from_internal_links": 153,
                            "page_from_size": 430995,
                            "page_from_encoding": "utf-8",
                            "page_from_language": "en",
                            "page_from_title": "From $6,000 to $73 billion: Warren Buffett’s wealth through the ages - MarketWatch",
                            "page_from_status_code": 200,
                            "first_seen": "2021-07-19 16:31:53 +00:00",
                            "prev_seen": "2023-01-11 11:44:45 +00:00",
                            "last_seen": "2023-03-12 15:06:53 +00:00",
                            "item_type": "anchor",
                            "attributes": null,
                            "dofollow": true,
                            "original": false,
                            "alt": null,
                            "image_url": null,
                            "anchor": "No. 3 on the U.S. rich list",
                            "text_pre": "According to the latest Forbes count, the so-called Oracle of Omaha is currently tipping the wealth scales at $73.1 billion.  That’s good enough to put Buffett, who turns 87 this summer, at",
                            "text_post": ", behind Microsoft’s MSFT,",
                            "semantic_location": "main",
                            "links_count": 1,
                            "group_count": 0,
                            "is_broken": false,
                            "url_to_status_code": 301,
                            "url_to_spam_score": 0,
                            "url_to_redirect_target": "https://www.forbes.com/pictures/gfgl45gfgf/warren-buffett/?ss=forbes400"
                            "ranked_keywords_info": {
                                "page_from_keywords_count_top_3": 8,
                                "page_from_keywords_count_top_10": 20,
                                "page_from_keywords_count_top_100": 234
                            },
                            "is_indirect_link": false,
                            "indirect_link_path": null
                        }
                    ],
                    "search_after_token": "eyJDdXJyZW50T2Zmc2V0IjowLCJSYXdSZXF1ZXN0Ijp7InRhcmdldCI6ImZvcmJlcy5jb20iLCJxdWVyeSI6eyJmaWVsZCI6ImRvZm9sbG93IiwidHlwZSI6ImVxIiwidmFsdWUiOnRydWV9LCJsaW1pdCI6NSwiYmFja2xpbmtzX3N0YXR1c190eXBlIjoibGl2ZSIsImluY2x1ZGVfc3ViZG9tYWlucyI6dHJ1ZSwibW9kZSI6ImFzX2lzIiwiYWlkIjoxNTM1fSwiU2VhcmNoQWZ0ZXJEYXRhIjp7IlZlcnNpb24iOjEsIlNlYXJjaEFmdGVyVmFsdWVzIjp7InJhbmsiOjY2NiwibGFzdF9zZWVuIjoiMjAyMy0wMy0xMlQxNTowNjo1MyswMDowMCJ9LCJUb2tlblJlYWxPZmZzZXQiOjV9fQ=="
                }
            ]
        }
    ]
}

POST https://api.dataforseo.com/v3/backlinks/backlinks/live
 Your account will be charged for each request.
The cost can be calculated on the Pricing page.
All POST data should be sent in the JSON format (UTF-8 encoding). The task setting is done using the POST method. When setting a task, you should send all task parameters in the task array of the generic POST array. You can send up to 2000 API calls per minute. The maximum number of requests that can be sent simultaneously is limited to 30.

You can specify the number of results you want to retrieve, filter and sort them.

Below you will find a detailed description of the fields you can use for setting a task.

Description of the fields for setting a task:

Field name	Type	Description
target	string	domain, subdomain or webpage to get backlinks for
required field
a domain or a subdomain should be specified without https:// and www.
a page should be specified with absolute URL (including http:// or https://)
mode	string	results grouping type
optional field
possible grouping types:
as_is – returns all backlinks
one_per_domain – returns one backlink per domain
one_per_anchor – returns one backlink per anchor
default value: as_is

custom_mode	object	detailed results grouping type
optional field
use this object to get a specific number of backlinks per field
if you use custom_mode, then mode will be ignored
example:
"custom_mode": {"field": "domain", "value": 100}
        field	string	response field
required field if you choose to specify custom_mode
possible values:
anchor
domain_from
domain_from_country
tld_from
page_from_encoding
page_from_language
item_type
page_from_status_code
semantic_location
        value	integer	number of backlinks to return per field
required field if you choose to specify custom_mode
can be set from 1 to 1000
filters	array	array of results filtering parameters
optional field
you can add several filters at once (8 filters maximum)
you should set a logical operator and, or between the conditions
the following operators are supported:
regex, =, <>, in, not_in, like, not_like, ilike, not_ilike, regex, not_regex
you can use the % operator with like and not_like to match any string of zero or more characters
example:
["rank",">","80"]
[["page_from_rank",">","55"],
"and",
["dofollow","=",true]]

[["first_seen",">","2017-10-23 11:31:45 +00:00"],
"and",
[["anchor","like","%seo%"],"or",["text_pre","like","%seo%"]]]

The full list of possible filters is available here.

order_by	array	results sorting rules
optional field
you can use the same values as in the filters array to sort the results
possible sorting types:
asc – results will be sorted in the ascending order
desc – results will be sorted in the descending order
you should use a comma to set up a sorting type
example:
["rank,desc"]
note that you can set no more than three sorting rules in a single request
you should use a comma to separate several sorting rules
example:
["domain_from_rank,desc","page_from_rank,asc"]
offset	integer	offset in the results array of the returned backlinks
optional field
default value: 0
if you specify the 10 value, the first ten backlinks in the results array will be omitted and the data will be provided for the successive backlinks;
Note: the maximum value is 20,000, use the search_after_token if you would like to offset more results

search_after_token	string	token for subsequent requests
optional field
provided in the identical filed of the response to each request;
use this parameter to avoid timeouts while trying to obtain over 100,000 results in a single request;
by specifying the unique search_after_token value from the response array, you will get the subsequent results of the initial task;
search_after_token values are unique for each subsequent task
Note: if the search_after_token is specified in the request, all other parameters should be identical to the previous request
limit	integer	the maximum number of returned backlinks
optional field
default value: 100
maximum value: 1000

backlinks_status_type	string	set what backlinks to return and count
optional field
you can use this field to choose what backlinks will be returned and used for aggregated metrics for your target;
possible values:
all – all backlinks will be returned and counted;
live – backlinks found during the last check will be returned and counted;
lost – lost backlinks will be returned and counted;
default value: live

include_subdomains	boolean	indicates if the subdomains of the target will be included in the search
optional field
if set to false, the subdomains will be ignored
default value: true
include_indirect_links	boolean	indicates if indirect links to the target will be included in the results
optional field
if set to true, the results will include data on indirect links pointing to a page that either redirects to the target, or points to a canonical page
if set to false, indirect links will be ignored
default value: true
exclude_internal_backlinks	boolean	indicates if internal backlinks from subdomains to the target will be excluded from the results
optional field
if set to true, the results will not include data on internal backlinks from subdomains of the same domain as target
if set to false, internal links will be included in the results
default value: true
tag	string	user-defined task identifier
optional field
the character limit is 255
you can use this parameter to identify the task and match it with the result
you will find the specified tag value in the data object of the response
‌

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
            target	string	target domain in a POST array
            mode	string	mode specified in a POST array
            custom_mode	object	custom mode specified in a POST array
            total_count	integer	total amount of results relevant the request
            items_count	integer	the number of results returned in the items array
            items	array	contains relevant backlinks and referring domains data
                type	string	type of element = ‘backlink’
                domain_from	string	domain referring to the target domain or webpage
                url_from	string	URL of the page where the backlink is found
                url_from_https	boolean	indicates whether the referring URL is secured with HTTPS
if true, the referring URL is secured with HTTPS
                domain_to	string	domain the backlink is pointing to
                url_to	string	URL the backlink is pointing to
                url_to_https	boolean	indicates if the URL the backlink is pointing to is secured with HTTPS
if true, the URL is secured with HTTPS
                tld_from	string	top-level domain of the referring URL
                is_new	boolean	indicates whether the backlink is new
if true, the backlink was found on the page last time our crawler visited it
                is_lost	boolean	indicates whether the backlink was removed
if true, the backlink or the entire page was removed
                backlink_spam_score	integer	spam score of the backlink
learn more about how the metric is calculated on this help center page
                rank	integer	backlink rank
rank that the given backlink passes to the target
rank is calculated based on the method for node ranking in a linked database – a principle used in the original Google PageRank algorithm
learn more about the metric and how it is calculated in this help center article
                page_from_rank	integer	page rank of the referring page
page_from_rank is calculated based on the method for node ranking in a linked database – a principle used in the original Google PageRank algorithm
learn more about the metric and how it is calculated in this help center article
                domain_from_rank	integer	domain rank of the referring domain
domain_from_rank is calculated based on the method for node ranking in a linked database – a principle used in the original Google PageRank algorithm
learn more about the metric and how it is calculated in this help center article
                domain_from_platform_type	array	platform types of the referring domain
example:
"cms",
"blogs"
                domain_from_is_ip	boolean	indicates if the domain is IP
if true, the domain functions as an IP address and does not have a domain name
                domain_from_ip	string	IP address of the referring domain
                domain_from_country	string	ISO country code of the referring domain
                page_from_external_links	integer	number of external links found on the referring page
                page_from_internal_links	integer	number of internal links found on the referring page
                page_from_size	integer	size of the referring page, in bytes
example:
63357
                page_from_encoding	string	character encoding of the referring page
example:
utf-8
                page_from_language	string	language of the referring page
in ISO 639-1 format
example:
en
                page_from_title	string	title of the referring page
                page_from_status_code	integer	HTTP status code returned by the referring page
example:
200
                first_seen	string	date and time when our crawler found the backlink for the first time
in the UTC format: “yyyy-mm-dd hh-mm-ss +00:00”
example:
2019-11-15 12:57:46 +00:00
                prev_seen	string	previous to the most recent date when our crawler visited the backlink
in the UTC format: “yyyy-mm-dd hh-mm-ss +00:00”
example:
2019-11-15 12:57:46 +00:00
                last_seen	string	most recent date when our crawler visited the backlink
in the UTC format: “yyyy-mm-dd hh-mm-ss +00:00”
example:
2019-11-15 12:57:46 +00:00
                item_type	string	link type
possible values:
anchor, image, meta, canonical, alternate, redirect
                attributes	array	link attributes of the referring links
example:
nofollow
                dofollow	boolean	indicates whether the backlink is dofollow
if false, the backlink is nofollow
                original	boolean	indicates whether the backlink was present on the referring page when our crawler first visited it
                alt	string	alternative text of the image
this field will be null if backlink type is not image
                image_url	string	URL of the image
the URL leading to the image on the original resource or DataForSEO storage (in case the original source is not available)
                anchor	string	anchor text of the backlink
                text_pre	string	snippet before the anchor text
                text_post	string	snippet after the anchor text
                semantic_location	string	indicates semantic element in HTML where the backlink is found
you can get the full list of semantic elements here
examples:
article, section, summary
                links_count	integer	number of identical backlinks found on the referring page
                group_count	integer	indicates total number of backlinks from this domain
for example, if mode is set to one_per_domain, this field will indicate the total number of backlinks coming from this domain
                is_broken	boolean	indicates whether the backlink is broken
if true, the backlink is pointing to a page responding with a 4xx or 5xx status code
                url_to_status_code	integer	status code of the referenced page
if the value is null, our crawler hasn’t yet visited the webpage the link is pointing to
example:
200
                url_to_spam_score	integer	spam score of the referenced page
if the value is null, our crawler hasn’t yet visited the webpage the link is pointing to;
learn more about how the metric is calculated on this help center page
                url_to_redirect_target	string	target url of the redirect
target page the redirect is pointing to
                ranked_keywords_info	object	number of keywords for which the page is ranked in top search results
                    page_from_keywords_count_top_3	integer	number of keywords for which the page is ranked in top 3 search results
                    page_from_keywords_count_top_10	integer	number of keywords for which the page is ranked in top 10 search results
                    page_from_keywords_count_top_100	integer	number of keywords for which the page is ranked in top 100 search results
                is_indirect_link	boolean	indicates whether the backlink is an indirect link
if true, the backlink is an indirect link pointing to a page that either redirects to url_to, or points to a canonical page
                indirect_link_path	array	indirect link path
indicates a URL or a sequence of URLs that lead to url_to
                    type	string	indirect link type
possible values: redirect, canonical
                    status_code	integer	HTTP status code of the URL
                    url	string	indirect link URL
            search_after_token	string	token for subsequent requests
by specifying the unique search_after_token when setting a new task, you will get the subsequent results of the initial task;
search_after_token values are unique for each subsequent task
‌‌

