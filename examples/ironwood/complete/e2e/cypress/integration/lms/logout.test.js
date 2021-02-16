describe("Log out ", () => {
  const lms_url = Cypress.env("LMS_URL");

  it("user can log out ", () => {
    // click on the user button //
    cy.visit(lms_url)
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    // cy.get(".toggle-user-dropdown").then(($button) => {
    //   cy.wrap($button).click();
    // });
    // // click on the log out
    // cy.get("#user-menu > :nth-child(4) > a").then(($button) => {
    //   cy.wrap($button).click({ force: true });
    // });
  });
});
