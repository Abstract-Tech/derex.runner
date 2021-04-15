describe("checkcourse test", () => {
  const lms_url = Cypress.env("LMS_URL");
  const cms_url = Cypress.env("CMS_URL");

  it("user can check the course", () => {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit(cms_url);
    cy.createCourse();
    cy.wait(2000);
    cy.visit(`${lms_url}/courses`);
    // enter to the first course on the list
    cy.get("body")
      .find("ul.courses-listing.courses-list")
      .then((res) => {
        if (res[0].children.length > 0) {
          cy.get("li.courses-listing-item").first().click();
          cy.get("body")
            .find("div.main-cta")
            .then((res) => {
              if (cy.get(res).children().length > 0) {
                cy.get(".register").then(($button) => {
                  cy.wrap($button).click();
                });
              } else {
                cy.get("strong").then(($button) => {
                  cy.wrap($button).click();
                });
              }
            });

          cy.get(".form-actions > .action-resume-course")
            .contains("Start Course")
            .then(($button) => {
              cy.wrap($button).click();
            });
        }
      });
  });
});
