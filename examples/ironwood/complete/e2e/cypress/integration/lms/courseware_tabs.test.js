describe("Knowledge Base Application", () => {
  it(` As a logged in user I should be able to access the "Wiki, Progrss, Instructor, Discussion" tab of the courseware of a course i'm enrolled in `, function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.get(".toggle-user-dropdown").then(($button) => {
      cy.wrap($button).click();
    });

    // the course number 14 on the dashbord

    cy.get(
      "#course-card-0 > .details > .wrapper-course-details > .wrapper-course-actions > .course-actions > .course-target-link"
    ).then(($button) => {
      cy.wrap($button).click();
    });
    // move to Description tab
    cy.get("#content > .navbar > .navbar-nav > :nth-child(4) > .nav-link").then(
      ($button) => {
        cy.wrap($button).click();
      }
    );

    // move to Progrss tab
    cy.get(".tabs > :nth-child(3) > a").then(($button) => {
      cy.wrap($button).click();
    });
    // move to Instructor tab
    cy.get(".tabs > :nth-child(5) > a").then(($button) => {
      cy.wrap($button).click();
    });
    // move to Discussion tab
    cy.get(".tabs > :nth-child(2) > a").then(($button) => {
      cy.wrap($button).click();
    });
  });
});
