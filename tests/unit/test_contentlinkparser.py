from webtoolkit import ContentLinkParser

from webtoolkit.tests.fakeinternet import FakeInternetTestCase


"""
#x22 - " character
#x3c - < character
"""

contents_with_links = """
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charSet="utf-8"/>
        "09 jan. 2024 02:00"
    </head>
    <body>
      <a href="https://www.youtube.com">YouTube domain</a>
      <a href="https://www.youtube.com:443">YouTube domain with port</a>
      <a href="https://www.youtube.com:443/location">YouTube domain with port, and location</a>
      <a href="https://www.youtube.com/location">YouTube domain, and location</a>
      <a href="https://www.youtube.com/location?v=12323&test=q#whatever">YouTube domain, and location</a>
      <a href="https://linkedin.com/location">Linkedin with location</a>
      <a href="from?site=github.com/bellard">From</a>
      <a href="//test.com/location">Test.com with location</a>
      <a href="/location">This page with location</a>
      <a href="location">This page with location</a>
      <a href="https:&#x2F;&#x2F;www.cedarpolicy.com" rel="nofollow">https:&#x2F;&#x2F;www.cedarpolicy.com</a>
      <a href="https:&#x2F;&#x2F;old.reddit.com&#x2F;r&#x2F;Oberon&#x2F;comments" rel="nofollow">Text</a>
      <a href="mailto:renegat@renegat0x0.ddns.net">Mailto</a>
      <a href="https:&#x2F;&#x2F;encoded.link.com&#x2F;product-page&#x2F;interceptor-carrier-board">Link</a>
      <a href="https:&#x2F;&#x2F;encoded.link2.com&#x22;product-page">Link</a>
      <a href="https:&#x2F;&#x2F;encoded.link3.com&#x3c;product-page">Link</a>

      <a href="https://">unknown</a>
      <a href="http://">unknown</a>

    </body>
</html>
"""


class ContentLinkParserTest(FakeInternetTestCase):
    def test_get_links(self):
        p = ContentLinkParser(
            "https://test_get_links.com/test",
            contents_with_links,
        )

        links = p.get_links()
        for link in links:
            print(link)

        self.assertTrue("https://www.youtube.com" in links)
        self.assertTrue("https://www.youtube.com:443" in links)
        self.assertTrue("https://www.youtube.com:443/location" in links)
        self.assertTrue("https://www.youtube.com/location" in links)
        self.assertTrue("https://www.youtube.com/location?v=12323&test=q#whatever" in links)
        self.assertTrue("https://linkedin.com/location" in links)
        self.assertTrue("https://test_get_links.com/test/from?site=github.com/bellard" in links)
        self.assertTrue("https://test.com/location" in links)
        self.assertTrue("https://test_get_links.com/location" in links)
        self.assertTrue("https://test_get_links.com/test/location" in links)
        self.assertTrue("https://renegat0x0.ddns.net" in links)
        self.assertTrue("https://www.cedarpolicy.com" in links)
        self.assertTrue("https://old.reddit.com/r/Oberon/comments" in links)
        self.assertTrue("https://encoded.link.com/product-page/interceptor-carrier-board" in links)
        self.assertTrue("https://encoded.link2.com" in links)
        self.assertTrue("https://encoded.link3.com" in links)
        self.assertEqual(len(links), 16)
        self.assertTrue("https://" not in links)
        self.assertTrue("http://" not in links)

    def test_get_domains(self):
        p = ContentLinkParser(
            "https://test_get_links.com/test",
            contents_with_links,
        )

        domains = p.get_domains()
        for link in domains:
            print(link)

        self.assertTrue("https://www.youtube.com" in domains)
        self.assertTrue("https://linkedin.com" in domains)
        self.assertTrue("https://test.com" in domains)
        self.assertTrue("https://test_get_links.com" in domains)
        self.assertTrue("https://renegat0x0.ddns.net" in domains)
        self.assertTrue("https://www.cedarpolicy.com" in domains)
        self.assertTrue("https://old.reddit.com" in domains)
        self.assertTrue("https://encoded.link.com" in domains)
        self.assertTrue("https://encoded.link2.com" in domains)
        self.assertTrue("https://encoded.link3.com" in domains)
        self.assertEqual(len(domains), 10)
        self.assertTrue("https://" not in domains)
        self.assertTrue("http://" not in domains)
        self.assertTrue("https://www.youtube.com:443" not in domains)
