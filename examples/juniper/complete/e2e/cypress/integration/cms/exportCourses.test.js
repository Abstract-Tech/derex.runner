describe("Studio home page", () => {
  const cms_url = Cypress.env("CMS_URL");
  const lms_url = Cypress.env("LMS_URL");
  const course_id = Cypress.env("DEMO_COURSE_ID");
  const export_url = `${cms_url}/export/${course_id}`;
  it("test if an Admin able import course", async () => {
    cy.visit(lms_url);
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit(export_url);
    cy.wait(2000);
    cy.get(".title > .list-actions > .item-action > .action").click({
      force: "true",
    });
    cy.wait(4000);
    cy.get("#download-exported-button").click({ force: "true" });
  });
});
