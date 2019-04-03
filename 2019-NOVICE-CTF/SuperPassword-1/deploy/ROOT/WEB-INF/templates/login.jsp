<%--
  Created by IntelliJ IDEA.
  User: symol
  Date: 19-3-17
  Time: 下午8:45
  To change this template use File | Settings | File Templates.
--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>Super Password</title>
    <link rel="stylesheet" href="bundle?file=bootstrap.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="#">Super Password 1</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar-main" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbar-main">
            <ul class="navbar-nav mr-auto">
                <li class="nav-item active">
                    <a class="nav-link" href="<%= request.getContextPath() + "/login" %>">登录</a>
                </li>
            </ul>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="row">
            <div class="col col-md-6 offset-md-3">
                <%
                    String msg = (String)request.getAttribute("msg");
                    if (msg != null) {
                %>
                <div class="alert alert-primary" role="alert">
                    <%= msg %>
                </div>
                <% } %>
                <h2>输入超级密码</h2>
                <form method="post">
                    <div class="form-group">
                        <label for="token">Token</label>
                        <input type="text" class="form-control" id="token" name="token" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            </div>
        </div>
    </div>
    <script src="bundle?file=jquery-3.3.1.slim.min.js,bootstrap.min.js"></script>
</body>
</html>
