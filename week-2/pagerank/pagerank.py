import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    prop_dist = {}
    all_pages = list(corpus.keys())
    linked_pages = corpus[page]
    num_pages = len(all_pages)

    random_factor = (1 - damping_factor) / num_pages

    if not linked_pages:
        for key in all_pages:
            prop_dist[key] = 1 / num_pages
    else:
        num_linked_pages = len(linked_pages)
        linked_page_prob = damping_factor / num_linked_pages

        for key in all_pages:
            prop_dist[key] = random_factor
            if key in linked_pages:
                prop_dist[key] += linked_page_prob

    return prop_dist

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    samples_dict = {page: 0 for page in corpus}
    sample = random.choice(list(corpus.keys()))

    for _ in range(n):
        dist = transition_model(corpus, sample, damping_factor)
        pages, weights = zip(*dist.items())
        sample = random.choices(pages, weights, k=1)[0]

        samples_dict[sample] += 1

    for page in samples_dict:
        samples_dict[page] /= n

    return samples_dict



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    num_pages = len(corpus)
    ranks = {page: 1 / num_pages for page in corpus}

    # Calculate initial page ranks evenly
    convergence_threshold = 0.001
    is_converged = False

    while not is_converged:
        new_ranks = {}
        for page in corpus:
            new_rank = (1 - damping_factor) / num_pages
            # Sum the page rank contributions from each linking page
            for other_page in corpus:
                if page in corpus[other_page] or len(corpus[other_page]) == 0:
                    links_count = len(corpus[other_page]) if len(corpus[other_page]) > 0 else num_pages
                    new_rank += damping_factor * ranks[other_page] / links_count
            new_ranks[page] = new_rank

        # Check for convergence
        is_converged = all(abs(new_ranks[page] - ranks[page]) < convergence_threshold for page in corpus)
        ranks = new_ranks.copy()

    return ranks


if __name__ == "__main__":
    main()
