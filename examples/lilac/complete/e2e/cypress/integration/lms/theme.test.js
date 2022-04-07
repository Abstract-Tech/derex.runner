describe("Theme tests", () => {
  beforeEach(() => {
    cy.visit(Cypress.env("LMS_URL"));
  });

  it("The header logo should be the theme logo", function () {
    cy.get(".logo")
      .should("have.attr", "src")
      .and("match", RegExp("/static/demo-theme/images/logo(.\\w+)?.png"));
  });

  it("The footer logo should be the theme logo", function () {
    cy.get(".wrapper-logo > p > a > img")
      .should("have.attr", "src")
      .and(
        "match",
        RegExp(
          `${Cypress.env(
            "LMS_URL"
          )}/static/demo-theme/images/logo(\.\\w+)?\.png`
        )
      );
  });

  it("The footer should contain footer navigation links", function () {
    cy.get("#about").should("have.attr", "href", "/about");
    cy.get("#blog").should("have.attr", "href", "/blog");
    cy.get("#contact").should("have.attr", "href", "/support/contact_us");
    cy.get("#donate").should("have.attr", "href", "/donate");
  });

  it("The footer Open edX logo should be visible", function () {
    cy.get(".footer-about-openedx > p > a > img").compareSnapshot(
      "openedx-footer-logo",
      0.2
    );
  });
});
