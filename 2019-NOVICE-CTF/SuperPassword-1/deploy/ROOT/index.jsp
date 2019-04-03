<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%
    String redirectURL = request.getContextPath() + "/login";
    response.sendRedirect(redirectURL);
%>