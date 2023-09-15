// Function to filter and display cards based on the search query
function filterCards(searchQuery) {
  var cardContainer = document.querySelector('.card-container');
  var cards = cardContainer.querySelectorAll('.card');

  cards.forEach(function (card) {
      var title = card.querySelector('h3').textContent.toLowerCase();
      var author = card.querySelector('.author').textContent.toLowerCase();

      if (title.includes(searchQuery.toLowerCase()) || author.includes(searchQuery.toLowerCase())) {
          card.style.display = 'flex'; // Show the card if it matches the search query, 
      } else {
          card.style.display = 'none'; // Hide the card if it doesn't match the search query
      }
  });
}

// Event listener for the search input field
var searchInput = document.querySelector('input[name="search_query"]');
searchInput.addEventListener('input', function () {
  var searchQuery = searchInput.value.trim();
  filterCards(searchQuery);
});

// Function to handle page load and initial setup
function handlePageLoad() {
  // Add event listener to the search input field
  searchInput.addEventListener('input', function () {
      var searchQuery = searchInput.value.trim();
      filterCards(searchQuery);
  });

  console.log('All scripts loaded!');
}

// Call the handlePageLoad function when the window has finished loading the page
window.onload = handlePageLoad;
