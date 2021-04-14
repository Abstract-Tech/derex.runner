describe("checkcourse test", () => {
  const lms_url = Cypress.env("LMS_URL");
  const mailslurper_url = Cypress.env("MAILSLURPER_URL");

  it("user can check the course", () => {
    cy.login(lms_url, Cypress.env("user_email"), Cypress.env("user_password"));

    cy.visit("/courses");
    // enter to the first course on the list

    cy.get("body")
      .find("ul.courses-listing.courses-list")
      .then((res) => {
        if (res[0].children.length > 0) {
          cy.get(".course:nth-child(1)").click();

          cy.get(".register").then(($button) => {
            cy.wrap($button).click();
          });
          cy.get("strong").then(($button) => {
            cy.wrap($button).click();
          });

          cy.get(".form-actions > .action-resume-course")
            .contains("Start Course")
            .then(($button) => {
              cy.wrap($button).click();
            });
        } else {
          console.log("no courses");
        }
      });
  });
});
