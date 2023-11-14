describe('Web App Tests', () => {
    beforeEach(() => {
      // Assuming your app is hosted at http://localhost:5000
      cy.visit('http://localhost:5000');
    });
  
    it('should redirect organization user to profile-org page', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Check if the redirection to profile-org page happens
      cy.url().should('include', '/profile-org');
    });
  
    it('should display recommended and upcoming events for regular user', () => {
      // Assuming the user is logged in as a regular user
      cy.loginAsRegularUser();
  
      // Check if the recommended events section is visible
      cy.get('.recommended-events').should('be.visible');
  
      // Check if the upcoming events section is visible
      cy.get('.upcoming-events').should('be.visible');
    });
  
    it('should render event creation form for organization user', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the event creation page
      cy.visit('http://localhost:5000/event/create');
  
      // Check if the event creation form is rendered
      cy.get('form#event-form').should('be.visible');
    });
  
    it('should submit event creation form successfully', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the event creation page
      cy.visit('http://localhost:5000/event/create');
  
      // Fill in the event creation form
      cy.get('#location_place').type('Sample Place');
      // ... Fill in other form fields as needed
  
      // Submit the form
      cy.get('form#event-form').submit();
  
      // Check if the user is redirected to the event details page
      cy.url().should('include', '/event/');
    });
  
    it('should display event details page for regular user', () => {
      // Assuming the user is logged in as a regular user
      cy.loginAsRegularUser();
  
      // Navigate to the event details page (replace EVENT_ID with a valid event ID)
      cy.visit('http://localhost:5000/event/EVENT_ID');
  
      // Check if the event details are displayed
      cy.get('.event-details').should('be.visible');
    });
  
    it('should submit a comment on the event details page', () => {
      // Assuming the user is logged in
      cy.loginAsRegularUser();
  
      // Navigate to the event details page (replace EVENT_ID with a valid event ID)
      cy.visit('http://localhost:5000/event/EVENT_ID');
  
      // Fill in the comment form
      cy.get('#comment_content').type('This is a test comment');
  
      // Submit the comment form
      cy.get('form#comment-form').submit();
  
      // Check if the comment is visible on the page
      cy.contains('This is a test comment').should('be.visible');
    });
  
    // Add more tests for other functionalities as needed
  
  });
  