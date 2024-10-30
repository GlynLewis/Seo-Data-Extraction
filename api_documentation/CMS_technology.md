from client import RestClient
# You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
client = RestClient("login", "password")
post_data = dict()
# You can set only one task at a time
post_data[len(post_data)] = dict(
    target="dataforseo.com"
)
# POST /v3/domain_analytics/technologies/domain_technologies/live
response = client.post("/v3/domain_analytics/technologies/domain_technologies/live", post_data)
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
  "time": "1.2276 sec.",
  "cost": 0.01,
  "tasks_count": 1,
  "tasks_error": 0,
  "tasks": [
    {
      "id": "10171413-1535-0483-0000-cb6e2685e725",
      "status_code": 20000,
      "status_message": "Ok.",
      "time": "1.1653 sec.",
      "cost": 0.01,
      "result_count": 1,
      "path": [
        "v3",
        "domain_analytics",
        "technologies",
        "domain_technologies",
        "live"
      ],
      "data": {
        "api": "domain_analytics",
        "function": "domain_technologies",
        "se": "technologies",
        "target": "dataforseo.com"
      },
      "result": [
        {
          "type": "domain_technology_item",
          "domain": "dataforseo.com",
          "title": "Powerful API Stack For Data-Driven SEO Tools – DataForSEO",
          "description": "We provide comprehensive data solutions for SEO and SEM analytics via API. DataForSEO is a trusted partner for 750+ SEO software companies and agencies.",
          "meta_keywords": null,
          "domain_rank": 455,
          "last_visited": "2022-09-23 17:19:25 +00:00",
          "country_iso_code": "EE",
          "language_code": "en",
          "content_language_code": "en",
          "phone_numbers": [
            "+3726027642"
          ],
          "emails": [
            "info@dataforseo.com"
          ],
          "social_graph_urls": [
            "https://dataforseo.com"
          ],
          "technologies": {
            "web_development": {
              "javascript_libraries": [
                "Lightbox",
                "Underscore.js",
                "jQuery",
                "jQuery Migrate",
                "prettyPhoto"
              ],
              "programming_languages": [
                "PHP"
              ]
            },
            "add_ons": {
              "wordpress_plugins": [
                "EWWW Image Optimizer",
                "Responsive Lightbox & Gallery",
                "Slider Revolution",
                "Contact Form 7"
              ]
            },
            "servers": {
              "performance": [
                "EWWW Image Optimizer"
              ],
              "cdn": [
                "Cloudflare"
              ],
              "databases": [
                "MySQL"
              ]
            },
            "content": {
              "photo_galleries": [
                "Responsive Lightbox & Gallery"
              ],
              "cms": [
                "WordPress"
              ],
              "blogs": [
                "WordPress"
              ]
            },
            "media": {
              "photo_galleries": [
                "Responsive Lightbox & Gallery"
              ]
            },
            "location": {
              "maps": [
                "Google Maps"
              ]
            }
          }
        }
      ]
    }
  ]
}
