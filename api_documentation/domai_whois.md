
‌
This endpoint will provide you with Whois data enriched with backlink stats, and ranking and traffic info from organic and paid search results. Using this endpoint you will be able to get all these data for the domains matching the parameters you specify in the request.

Instead of ‘login’ and ‘password’ use your credentials from https://app.dataforseo.com/api-dashboard

            

from client import RestClient
# You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
client = RestClient("login", "password")
post_data = dict()
# simple way to set a task
post_data[len(post_data)] = dict(
    limit=10,
    filters=[
        ["domain", "like", "%seo%"],
        "and",
        ["metrics.organic.pos_1", ">", 200]
    ],
    order_by = ["metrics.organic.pos_1,desc"]
)
# POST /v3/domain_analytics/whois/overview/live
response = client.post("/v3/domain_analytics/whois/overview/live", post_data)
# you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
if response["status_code"] == 20000:
    print(response)
    # do something with result
else:
    print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


        

The above command returns JSON structured like this:


{
    "version": "0.1.20220819",
    "status_code": 20000,
    "status_message": "Ok.",
    "time": "1.3381 sec.",
    "cost": 0.102,
    "tasks_count": 1,
    "tasks_error": 0,
    "tasks": [
        {
            "id": "09051257-1535-0405-0000-4f0cc684968b",
            "status_code": 20000,
            "status_message": "Ok.",
            "time": "1.2886 sec.",
            "cost": 0.102,
            "result_count": 1,
            "path": [
                "v3",
                "domain_analytics",
                "whois",
                "overview",
                "live"
            ],
            "data": {
                "api": "domain_analytics",
                "function": "overview",
                "limit": 2,
                "filters": [
                    [
                        "epp_status_codes",
                        "in",
                        [
                            "client_transfer_prohibited",
                            "client_update_prohibited"
                        ]
                    ]
                ]
            },
            "result": [
                {
                    "total_count": 52989341,
                    "items_count": 2,
                    "items": [
                        {
                            "domain": "wikipedia.org",
                            "created_datetime": "2001-01-12 22:12:14 +00:00",
                            "changed_datetime": "2020-10-15 19:29:57 +00:00",
                            "expiration_datetime": "2023-01-12 22:12:14 +00:00",
                            "updated_datetime": "2021-04-16 11:52:41 +00:00",
                            "first_seen": "2020-10-06 21:00:00 +00:00",
                            "epp_status_codes": [
                                "client_delete_prohibited",
                                "client_transfer_prohibited",
                                "client_update_prohibited"
                            ],
                            "tld": "org",
                            "registered": true,
                            "registrar": null,
                            "metrics": {
                                "organic": {
                                    "pos_1": 35658587,
                                    "pos_2_3": 32908196,
                                    "pos_4_10": 47313535,
                                    "pos_11_20": 41082282,
                                    "pos_21_30": 31014870,
                                    "pos_31_40": 26330832,
                                    "pos_41_50": 23440124,
                                    "pos_51_60": 20841011,
                                    "pos_61_70": 19548812,
                                    "pos_71_80": 18046963,
                                    "pos_81_90": 16082534,
                                    "pos_91_100": 9175823,
                                    "etv": 23900310990.23806,
                                    "impressions_etv": 771436611.1198553,
                                    "count": 321444096,
                                    "estimated_paid_traffic_cost": 79567794585.6828
                                },
                                "paid": {
                                    "pos_1": 8,
                                    "pos_2_3": 1,
                                    "pos_4_10": 0,
                                    "pos_11_20": 0,
                                    "pos_21_30": 0,
                                    "pos_31_40": 0,
                                    "pos_41_50": 0,
                                    "pos_51_60": 0,
                                    "pos_61_70": 0,
                                    "pos_71_80": 0,
                                    "pos_81_90": 0,
                                    "pos_91_100": 0,
                                    "etv": 169.81799960136414,
                                    "impressions_etv": 0,
                                    "count": 9,
                                    "estimated_paid_traffic_cost": 1027.9993352890015
                                }
                            },
                            "backlinks_info": {
                                "referring_domains": 10194664,
                                "referring_main_domains": 5757246,
                                "referring_pages": 5313948233,
                                "dofollow": 4849266257,
                                "backlinks": 6520586114,
                                "time_update": "2022-08-24 06:05:35 +00:00"
                            }
                        },
                        {
                            "domain": "facebook.com",
                            "created_datetime": "1997-03-29 03:00:00 +00:00",
                            "changed_datetime": "2020-03-10 16:53:59 +00:00",
                            "expiration_datetime": "2028-03-30 01:00:00 +00:00",
                            "updated_datetime": "2021-06-11 16:57:33 +00:00",
                            "first_seen": "2020-10-06 21:00:00 +00:00",
                            "epp_status_codes": [
                                "client_delete_prohibited",
                                "client_transfer_prohibited",
                                "client_update_prohibited",
                                "server_delete_prohibited",
                                "server_transfer_prohibited",
                                "server_update_prohibited"
                            ],
                            "tld": "com",
                            "registered": true,
                            "registrar": null,
                            "metrics": {
                                "organic": {
                                    "pos_1": 5576594,
                                    "pos_2_3": 28738213,
                                    "pos_4_10": 59757370,
                                    "pos_11_20": 57280488,
                                    "pos_21_30": 43103470,
                                    "pos_31_40": 33916597,
                                    "pos_41_50": 26207641,
                                    "pos_51_60": 20256621,
                                    "pos_61_70": 16229490,
                                    "pos_71_80": 12998026,
                                    "pos_81_90": 10383074,
                                    "pos_91_100": 5875411,
                                    "etv": 9572697872.175035,
                                    "impressions_etv": 671052062.6383919,
                                    "count": 320323263,
                                    "estimated_paid_traffic_cost": 29717359040.347725
                                },
                                "paid": {
                                    "pos_1": 13295,
                                    "pos_2_3": 2684,
                                    "pos_4_10": 643,
                                    "pos_11_20": 1,
                                    "pos_21_30": 0,
                                    "pos_31_40": 0,
                                    "pos_41_50": 0,
                                    "pos_51_60": 0,
                                    "pos_61_70": 0,
                                    "pos_71_80": 0,
                                    "pos_81_90": 0,
                                    "pos_91_100": 0,
                                    "etv": 42447788.124515526,
                                    "impressions_etv": 4397999.777682677,
                                    "count": 16623,
                                    "estimated_paid_traffic_cost": 45094463.5356169
                                }
                            },
                            "backlinks_info": {
                                "referring_domains": 65469011,
                                "referring_main_domains": 33563324,
                                "referring_pages": 77405607961,
                                "dofollow": 66351150396,
                                "backlinks": 99337131695,
                                "time_update": "2022-08-24 18:27:48 +00:00"
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

POST https://api.dataforseo.com/v3/domain_analytics/whois/overview/live
 Your account will be charged for each request.
The cost can be calculated on the Pricing page.
All POST data should be sent in the JSON format (UTF-8 encoding). The task setting is done using the POST method. When setting a task, you should send all task parameters in the task array of the generic POST array. You can send up to 2000 API calls per minute.

You can specify the number of results you want to retrieve, set filters and indicate sorting parameters.

Below you will find a detailed description of the fields you can use for setting a task.

Description of the fields for setting a task:

Field name	Type	Description
limit	integer	the maximum number of returned domains
optional field
default value: 100
maximum value: 1000
offset	integer	offset in the results array of returned items
optional field
default value: 0
if you specify the 10 value, the first ten items in the results array will be omitted and the data will be provided for the successive items
filters	array	array of results filtering parameters
optional field
you can add several filters at once (8 filters maximum)
you should set a logical operator and, or between the conditions
the following operators are supported:
regex, <, <=, >, >=, =, <>, in, not_in, like, not_like
you can use the % operator with like and not_like to match any string of zero or more characters
examples:
["expiration_datetime", "<", "2021-02-15 01:00:00 +00:00"]
[["expiration_datetime", "<", "2021-02-15 01:00:00 +00:00"], "and", ["domain", "like", "%seo%"]]

for more information about filters, please refer to Filters Page or this help center guide

order_by	array	results sorting rules
optional field
you can use the same values as in the filters array to sort the results
possible sorting types:
asc - results will be sorted in the ascending order
desc - results will be sorted in the descending order
the comma is used as a separator
example:
["metrics.organic.pos_1,desc"]
default rule:
["metrics.organic.count,desc"]
note that you can set no more than three sorting rules in a single request
you should use a comma to separate several sorting rules
example:
["expiration_datetime,asc","metrics.organic.etv,desc","metrics.organic.pos_1,desc"]
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
            total_count	integer	total amount of results in our database relevant to your request
            items_count	integer	the number of results returned in the items array
            items	array	contains ranking and traffic data
                domain	string	domain name
                created_datetime	string	date and time of registration
date and time (in the ISO 8601 format) when the domain was first registered
example:
"1997-03-29 03:00:00 +00:00"
                changed_datetime	string	date and time when the domain entry was changed
date and time (in the ISO 8601 format) when the domain entry was last modified
example:
"2021-01-14 08:36:28 +00:00"
                expiration_datetime	string	date and time when the domain will expire
date and time (in the ISO 8601 format) when the domain is due to expire
example:
"2022-11-26 17:21:23 +00:00"
                updated_datetime	string	date and time when the domain was updated
date and time (in the ISO 8601 format) when the domain was last updated
example:
"2021-01-29 13:59:38 +00:00"
                first_seen	string	date and time when our crawler found the domain for the first time
in the UTC format: “yyyy-mm-dd hh-mm-ss +00:00”
example:
"2019-11-15 12:57:46 +00:00"
                epp_status_codes	array	extensive provisioning protocol status codes
the status of a domain name registration as defined by ICANN
                tld	string	top-level domain
top-level domain in the DNS root zone
                registered	boolean	domain registration status
if false, the domain name registration has expired
Note: expired domains will remain in the database for only a short period of time
                registrar	string	domain registrar
if null, the domain registrar is unknown
example:
NameCheap, Inc.
                metrics	object	ranking data relevant to the specified domain
                    organic	object	ranking and traffic data from organic search
                        pos_1	integer	number of organic SERPs where the domain ranks #1
                        pos_2_3	integer	number of organic SERPs where the domain ranks #2-3
                        pos_4_10	integer	number of organic SERPs where the domain ranks #4-10
                        pos_11_20	integer	number of organic SERPs where the domain ranks #11-20
                        pos_21_30	integer	number of organic SERPs where the domain ranks #21-30
                        pos_31_40	integer	number of organic SERPs where the domain ranks #31-40
                        pos_41_50	integer	number of organic SERPs where the domain ranks #41-50
                        pos_51_60	integer	number of organic SERPs where the domain ranks #51-60
                        pos_61_70	integer	number of organic SERPs where the domain ranks #61-70
                        pos_71_80	integer	number of organic SERPs where the domain ranks #71-80
                        pos_81_90	integer	number of organic SERPs where the domain ranks #81-90
                        pos_91_100	integer	number of organic SERPs where the domain ranks #91-100
                        etv	float	estimated traffic volume
estimated organic monthly traffic to the domain
calculated as the product of CTR (click-through-rate) and search volume values of all keywords the domain ranks for
learn more about how the metric is calculated in this help center article
                        impressions_etv	float	estimated traffic volume based on impressions
estimated organic monthly traffic to the domain
calculated as the product of CTR (click-through-rate) and impressions values of all keywords the domain ranks for
learn more about how the metric is calculated in this help center article
                        count	integer	total count of organic SERPs that contain the domain
                        estimated_paid_traffic_cost	float	estimated cost of converting organic search traffic into paid
represents the estimated monthly cost of running ads (USD) for all keywords a domain ranks for
the metric is calculated as the product of organic etv and paid cpc values and indicates the cost of driving the estimated volume of monthly organic traffic through PPC advertising in Google Search
learn more about how the metric is calculated in this help center article
                    paid	object	ranking and traffic data from paid search
                        pos_1	integer	number of paid SERPs where the domain ranks #1
                        pos_2_3	integer	number of paid SERPs where the domain ranks #2-3
                        pos_4_10	integer	number of paid SERPs where the domain ranks #4-10
                        pos_11_20	integer	number of paid SERPs where the domain ranks #11-20
                        pos_21_30	integer	number of paid SERPs where the domain ranks #21-30
                        pos_31_40	integer	number of paid SERPs where the domain ranks #31-40
                        pos_41_50	integer	number of paid SERPs where the domain ranks #41-50
                        pos_51_60	integer	number of paid SERPs where the domain ranks #51-60
                        pos_61_70	integer	number of paid SERPs where the domain ranks #61-70
                        pos_71_80	integer	number of paid SERPs where the domain ranks #71-80
                        pos_81_90	integer	number of paid SERPs where the domain ranks #81-90
                        pos_91_100	integer	number of paid SERPs where the domain ranks #91-100
                        etv	float	estimated traffic volume
estimated paid monthly traffic to the domain
calculated as the product of CTR (click-through-rate) and search volume values of all keywords the domain ranks for
learn more about how the metric is calculated in this help center article
                        impressions_etv	float	estimated traffic volume based on impressions
Note that the data in the impressions_etv field is deprecated and provided only as legacy to avoid maintenance issues
estimated paid monthly traffic to the domain
calculated as the product of CTR (click-through-rate) and impressions values of all keywords the domain ranks for
learn more about how the metric is calculated in this help center article

                        count	integer	total count of paid SERPs that contain the domain
                        estimated_paid_traffic_cost	float	estimated cost of monthly search traffic
represents the estimated cost of paid monthly traffic (USD) based on etv and cpc values
learn more about how the metric is calculated in this help center article
                backlinks_info	object	backlink data for the returned domain
                    referring_domains	integer	number of referring domains
                    referring_main_domains	integer	number of referring main domains
                    referring_pages	integer	number of referring pages
                    dofollow	integer	number of dofollow links
                    backlinks	integer	total number of backlinks
the total number of backlinks, including dofollow and nofollow links
                    time_update	string	date and time when backlink data was updated
in the UTC format: "yyyy-mm-dd hh-mm-ss +00:00"
example:
2019-11-15 12:57:46 +00:00
‌‌