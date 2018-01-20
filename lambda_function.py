import os
import logging
import json
import datetime
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse


def lambda_handler(event, context):
    logger = logging.getLogger(__name__)

    webhook_url = os.environ.get('SLACK_INCOMING_WEBHOOK_URL')

    if webhook_url:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        url = 'https://medium.com/browse/top/{}-{}-{}'.format(
            yesterday.strftime('%B').lower(),
            yesterday.strftime('%d'), yesterday.strftime('%Y'))

        site = requests.get(url)

        content = BeautifulSoup(site.content, 'html.parser')
        postElements = content.select('.streamItem')

        posts = []
        for i, element in enumerate(postElements):
            # post title
            title = element.select('.graf--title')[0].get_text()
            title_link = element.select('.postArticle-content > a')[0].get(
                'href')

            # contents
            contents = element.select('.graf--trailing')[0].get_text()

            # timestamp
            date = element.select('time')[0].get_text()
            timestamp = parse(date).timestamp()

            # crap
            crap = element.select('.js-multirecommendCountButton')[
                0].get_text()

            # auther info
            authorElement = element.select('.postMetaInline-authorLockup > a')
            author = authorElement[0].get_text()
            author_link = authorElement[0].get('href')
            author_image = element.select('.avatar-image')[0].get('src')

            publisher = "<{}|{}>".format(
                authorElement[1].get('href'), authorElement[1].get_text()
            ) if len(authorElement) > 1 else "<https://medium.com/|Medium>"

            # post image
            imageElements = element.select('figure .graf-image')
            image = imageElements[0].get('src') if imageElements else ""

            posts.append({
                "pretext":
                "{}.".format(i + 1),
                "title":
                title,
                "title_link":
                title_link,
                "text":
                "{}\n<{}|`...`>".format(contents, title_link),
                "mrkdwn_in": ["text"],
                "author_name":
                author,
                "author_link":
                author_link,
                "author_icon":
                author_image,
                "image_url":
                image,
                # "text": "{}\n:clap: {}".format(publisher, crap),
                "fields": [{
                    "title": "Published from",
                    "value": publisher,
                    "short": True
                }, {
                    "title": ":clap:",
                    "value": crap,
                    "short": True
                }],
                "ts":
                timestamp
            })

        logger.debug(posts)

        data = {
            "text":
            "Most popular on January 16, 2018 {}".format(
                yesterday.strftime('%B %d, %Y')),
            "attachments":
            posts
        }
        response = requests.post(
            webhook_url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'})

        if response.status_code == requests.codes.ok:
            logger.info('success posting to slack')
        else:
            logger.info('fail posting to slack')
            response.raise_for_status()

    else:
        logger.error('cannot find a slack webhook url')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    lambda_handler(None, None)