describe("Knowledge Base Application", () => {
  beforeEach(() => {});

  let count = 0;

  const $click = ($el) => {
    count += 1;
    return $el.click();
  };
  it("change settings ", async () => {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));

    cy.visit(Cypress.env("CMS_URL"));

    // grab the first course on the list
    cy.get(".list-courses .course-item:nth-child(1)").wait(1000).click();
    cy.get(".nav-course-settings").wait(1000).click();
    cy.get(".nav-course-settings-advanced").wait(1000).click(); // grab the 24 item on the list
    // grab the thied item on the list
    /* Allow Anonymous Discussion Posts to Peers and check if it contains false */
    cy.get(
      ":nth-child(3) > .value > .CodeMirror > .CodeMirror-scroll > .CodeMirror-sizer .CodeMirror-lines pre .cm-atom"
    )
      .wait(1000)
      .contains("false");
    // grab the 24 item on the list
    /* Course Visibility In Catalog and check if it contains both */
    cy.get(
      ":nth-child(24) > .value > .CodeMirror > .CodeMirror-scroll > .CodeMirror-sizer .CodeMirror-lines pre .cm-string"
    )
      .wait(1000)
      .contains("both");
  });
});
