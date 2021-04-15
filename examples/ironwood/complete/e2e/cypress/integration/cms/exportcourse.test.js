describe("Export course", () => {
  const cms_url = Cypress.env("CMS_URL");
  const course_id = Cypress.env("DEMO_COURSE_ID");
  const export_url = `${cms_url}/export/${course_id}`;

  it("allows admin to export a course", () => {
    cy.login(cms_url, Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit(export_url);
    cy.get("a.action-export").click();
  });
});
