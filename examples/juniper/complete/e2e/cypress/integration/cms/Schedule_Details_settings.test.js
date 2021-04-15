describe("Knowledge Base Application", () => {
  // previous test omitted for brevity
  let count = 0;

  const $click = ($el) => {
    count += 1;
    return $el.click();
  };
  const cms_url = Cypress.env("CMS_URL");

  it("change sittings ", () => {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    // check the first on the list.
    cy.get(".list-courses .course-item:nth-child(1)").wait(1000).click();
    cy.get(".nav-course-settings").wait(1000).click();
    cy.get(".nav-course-settings-schedule").wait(1000).click();
    cy.get("#course-start-date").clear().type("01/01/2019");
    cy.get("#course-start-time").clear().type("01:00");
    cy.get("#course-end-date").clear().type("01/01/2020");
    cy.get("#course-end-time").clear().type("02:00");
    cy.get("#upload-course-image").wait(1000).click();
    cy.get(".upload-dialog > input").wait(1000).click();
  });
});
