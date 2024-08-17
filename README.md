# Web-crawler

An improvised version of the code given in https://www.zenrows.com/blog/web-crawler-python#what-is-a-web-crawler-in-python.

Improvised to include,
1) Multi-threading - to speed up the crawling process
2) JavaScript Execution - For pages relying heavily on JavaScript, use headless browsers to render and crawl dynamic content
3) Retry and Exception handling
4) Queue Management - Use scalable queue systems to manage large numbers of URLs
5) Hashing - Implement a content deduplication mechanism (e.g., hashing the content) to avoid storing duplicate data.
6) Finger printing - Use fingerprinting techniques to identify and filter out duplicate content
7) Real-time Monitoring - Set up real-time monitoring to track the crawler’s progress and identify any issues quickly
8) Throttle Requests - Adjust crawling speed based on the target site's load to avoid getting blocked
9) User agent managament - Rotate user agents to mimic different browsers and reduce the chances of getting blocked
10) Key word filtering - prioritize or exclude certain pages based on their content
11) Adaptive Crawling - heuristic method to adaptively decide which pages to crawl next based on their relevance or importance
12) CAPTCHA Handling - Implement solutions for handling CAPTCHAs
13) Proxy server rotation - To avoid IP bans and distribute requests across different IPs
14) Efficient Storage - Use efficient storage systems like MongoDB handling large volumes of crawled data
15) Data Cleaning - To ensure the stored data is relevant and free of noise
