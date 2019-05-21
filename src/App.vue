<template>
  <div id="app">
    <div class="container">
    <nav class="navbar navbar-toggleable-md navbar-inverse bg-inverse fixed-top">
  <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <router-link to="/" class="navbar-brand text-success active"> 简读</router-link>

  <div class="collapse navbar-collapse" id="navbarSupportedContent">
    <ul class="navbar-nav mr-auto">
      <li class="nav-item">
        <router-link to="/home" class="nav-link"><i class="fa fa-home"></i> Home</router-link>
      </li>
      <li class="nav-item">
        <router-link to="/articles" class="nav-link"><i class="fa fa-flag"></i>订阅文章</router-link>
      </li>
    </ul>
    <form class="form-inline my-2 my-lg-0">
      <input class="form-control mr-sm-2" type="text" placeholder="搜索公众号">
      <router-link to="/search"><i class="fa fa-search btn btn-outline-success my-2 my-sm-0" @click=""></i></router-link>
	<a href="/admin" title="后台管理"><i class="fa fa-user-o btn btn-outline-success"></i></a>
    </form>
  </div>
</nav>
    </div>
    <div class="container" style="margin-top: 80px">
      <div class="row">
        <div class="col-xs-12 col-md-3 col-xl-3 push-md-9 push-xl-9">
          <sidebar></sidebar>
        </div>
        <div class="col-xs-12 col-md-9 col-xl-9 pull-md-3 pull-xl-3">
          <router-view></router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
    import Siderbar from './components/Sidebar.vue'

    export default {
        components: {
            'sidebar': Siderbar
        }
    }
</script>