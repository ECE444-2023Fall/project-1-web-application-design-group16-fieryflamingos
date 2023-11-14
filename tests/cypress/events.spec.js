describe('Event Update and Delete Tests', () => {
    beforeEach(() => {
      // Assuming your app is hosted at http://localhost:5000
      cy.visit('http://localhost:5000');
    });
  
    it('should render event update form for organization user', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the event update page (replace EVENT_ID with a valid event ID)
      cy.visit('http://localhost:5000/event/update/EVENT_ID');
  
      // Check if the event update form is rendered
      cy.get('form#event-form').should('be.visible');
    });
  
    it('should submit event update form successfully', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the event update page (replace EVENT_ID with a valid event ID)
      cy.visit('http://localhost:5000/event/update/EVENT_ID');
  
      // Fill in the event update form
      cy.get('#location_place').clear().type('Updated Place');
      // ... Update other form fields as needed
  
      // Submit the form
      cy.get('form#event-form').submit();
  
      // Check if the user is redirected to the event details page
      cy.url().should('include', '/event/');
    });
  
    it('should render event delete confirmation page for organization user', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the event delete confirmation page (replace EVENT_ID with a valid event ID)
      cy.visit('http://localhost:5000/event/delete/EVENT_ID');
  
      // Check if the event delete confirmation message is visible
      cy.contains('Are you sure you want to delete this event?').should('be.visible');
    });
  
    it('should delete event successfully', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the event delete confirmation page (replace EVENT_ID with a valid event ID)
      cy.visit('http://localhost:5000/event/delete/EVENT_ID');
  
      // Click the delete button
      cy.get('button#delete-btn').click();
  
      // Check if the user is redirected to their profile page
      cy.url().should('include', '/profile-org');
    });
  
    // Add more tests for other functionalities as needed
  });
  