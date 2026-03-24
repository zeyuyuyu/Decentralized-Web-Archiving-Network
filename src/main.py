import os
import asyncio
import multiprocessing as mp
from dwan.agent import ArchiveAgent
from dwan.governance import GovernanceProtocol
from dwan.scraper import WebScraper

# Initialize the governance protocol
gov_protocol = GovernanceProtocol()

# Spawn a swarm of archive agents
agents = [ArchiveAgent(gov_protocol) for _ in range(100)]

# Create a swarm of web scrapers
scraper_swarm = [WebScraper(gov_protocol, agent) for agent in agents]

async def main():
    # Coordinate the scraper swarm to monitor and archive web content
    await asyncio.gather(*[scraper.run() for scraper in scraper_swarm])

if __name__ == '__main__':
    mp.set_start_method('spawn')
    asyncio.run(main())