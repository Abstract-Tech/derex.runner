describe("Knowledge Base Application", () => {
  const lms_url = Cypress.env("LMS_URL");
  const cms_url = Cypress.env("CMS_URL");

  // previous test omitted for brevity
  it("test after you logged in you are able to navigate to dashboard page and check if there is courses or not ", function () {
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
          cy.visit(`${lms_url}/dashboard`);
          cy.get("body")
            .find("ul.listing-courses")
            .then((res) => {
              if (res[0].children.length > 0) {
                cy.get(".course").should("be.visible");
              }
            });
        }
      });
  });
});
