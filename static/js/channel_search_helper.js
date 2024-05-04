// Get the search box element
const searchBox = document.getElementById('search-box');
const clearSearchBox = document.getElementById('clear-search-box');

// Get the results element
const results = document.getElementById('results');

clearSearchBox.addEventListener('click', () => {
  searchBox.value = '';
  searchBox.focus();
  searchBox.dispatchEvent(new Event('keyup'));
  return false;
});

// Add an event listener to the search box
searchBox.addEventListener('keyup', function () {
  // Get the search value
  const searchValue = this.value.toLowerCase();

  // Hide all the result divs
  results.querySelectorAll('.result').forEach(result => {
    result.style.display = 'none';
  });

  // Filter the result divs based on the search value
  const filteredResults = Array.from(results.querySelectorAll('.result')).filter(result => {
    const title = result.querySelector('h5').textContent.toLowerCase();
    const content = result.querySelector('p').textContent.toLowerCase();

    return title.includes(searchValue) || content.includes(searchValue);
  });

  // Show the filtered result divs
  filteredResults.forEach(result => {
    result.style.display = 'block';
  });
});