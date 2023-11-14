describe('Profile and Calendar Tests', () => {
    beforeEach(() => {
      // Assuming your app is hosted at http://localhost:5000
      cy.visit('http://localhost:5000');
    });
  
    it('should render regular user profile page', () => {
      // Assuming the user is logged in as a regular user
      cy.loginAsRegularUser();
  
      // Navigate to the regular user profile page
      cy.visit('http://localhost:5000/profile');
  
      // Check if the profile page is rendered
      cy.get('h1').should('contain', 'Profile');
    });
  
    it('should render organization user profile page', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the organization user profile page (replace USER_ID with a valid user ID)
      cy.visit('http://localhost:5000/profile-org/USER_ID');
  
      // Check if the organization user profile page is rendered
      cy.get('h1').should('contain', 'Organization Profile');
    });
  
    it('should update regular user profile successfully', () => {
      // Assuming the user is logged in as a regular user
      cy.loginAsRegularUser();
  
      // Navigate to the regular user profile edit page
      cy.visit('http://localhost:5000/profile/edit');
  
      // Fill in the update form
      cy.get('#first_name').clear().type('New First Name');
      // ... Update other form fields as needed
  
      // Submit the form
      cy.get('form#update-profile-form').submit();
  
      // Check if the user is redirected to the profile page
      cy.url().should('include', '/profile');
    });
  
    it('should update organization user profile successfully', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the organization user profile edit page
      cy.visit('http://localhost:5000/profile-org/edit');
  
      // Fill in the update form
      cy.get('#name').clear().type('New Organization Name');
      // ... Update other form fields as needed
  
      // Submit the form
      cy.get('form#update-profile-org-form').submit();
  
      // Check if the user is redirected to the profile page
      cy.url().should('include', '/profile-org');
    });
  
    it('should render regular user calendar page', () => {
      // Assuming the user is logged in as a regular user
      cy.loginAsRegularUser();
  
      // Navigate to the regular user calendar page
      cy.visit('http://localhost:5000/calendar');
  
      // Check if the calendar page is rendered
      cy.get('h1').should('contain', 'Calendar');
    });
  
    it('should render organization user calendar page', () => {
      // Assuming the user is logged in as an organization user
      cy.loginAsOrganizationUser();
  
      // Navigate to the organization user calendar page
      cy.visit('http://localhost:5000/calendar-org');
  
      // Check if the calendar page is rendered
      cy.get('h1').should('contain', 'Calendar');
    });
  
    // Add more tests for other functionalities as needed
  });
  